import ray
import asyncio
import json
import logging
import time
from typing import List, Dict, Optional
from confluent_kafka import Consumer, KafkaError, TopicPartition
from ray.util import ActorPool

logger = logging.getLogger(__name__)


@ray.remote
class KafkaConsumerActor:
    """
    Kafka消息消费Actor，基于Gemini方案设计
    - 使用ActorPool直接分发任务，无需中心化负载均衡器
    - 支持背压感知的消息处理
    - 专注于消息消费，业务逻辑交给下游处理
    """
    
    def __init__(self, 
                 partition_ids: List[int], 
                 buffer_manager_pool: ActorPool,
                 kafka_config: Dict,
                 batch_timeout_seconds: int = 10,
                 max_batch_size: int = 100):
        """
        初始化Kafka消费者
        
        Args:
            partition_ids: 负责的Kafka分区ID列表
            buffer_manager_pool: BufferManager Actor池
            kafka_config: Kafka配置
            batch_timeout_seconds: 批处理超时时间（秒），默认10秒
            max_batch_size: 最大批处理大小，默认100个用户
        """
        self.partition_ids = partition_ids
        self.manager_pool = buffer_manager_pool
        self.kafka_config = kafka_config
        self.consumer = None
        self.running = False
        
        # 统计信息
        self.stats = {
            'messages_consumed': 0,
            'messages_per_second': 0,
            'last_offset': {},
            'errors': 0,
            'batches_sent': 0,
            'unique_users_processed': 0,
            'time_triggered_batches': 0,
            'size_triggered_batches': 0,
            'empty_flush_skipped': 0  # 跳过的空批次数
        }
        
        # 批处理控制（可配置）
        self.user_events_buffer = {}  # {user_id: latest_event}
        self.last_batch_time = None
        self.batch_timeout_seconds = batch_timeout_seconds
        self.max_batch_size = max_batch_size
        
        self._init_consumer()
    
    def _init_consumer(self):
        """初始化Kafka消费者"""
        try:
            # confluent_kafka配置
            consumer_config = {
                'bootstrap.servers': ','.join(self.kafka_config.get('bootstrap_servers', ['localhost:9092'])),
                'group.id': 'memory_processing_group',
                'auto.offset.reset': 'latest',
                'enable.auto.commit': True,
                'auto.commit.interval.ms': 5000,
                'session.timeout.ms': 30000,
                'heartbeat.interval.ms': 3000,
                'max.poll.interval.ms': 300000,
                'fetch.min.bytes': 1024,
                'fetch.wait.max.ms': 500,
                'api.version.request': True,
                'client.id': f'memory_processor_consumer_{id(self)}'
            }
            
            # 创建消费者
            self.consumer = Consumer(consumer_config)
            
            # 手动分配分区
            topic = self.kafka_config.get('topics', ['buffer_zone_cdc'])[0]
            partitions = [TopicPartition(topic, pid) for pid in self.partition_ids]
            self.consumer.assign(partitions)
            
            logger.info(f"Confluent Kafka consumer initialized for partitions: {self.partition_ids}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Confluent Kafka consumer: {e}")
            raise
    
    async def start_consuming(self):
        """开始消费消息 - 优化版本，支持用户去重和时间控制"""
        self.running = True
        self.last_batch_time = time.time()
        logger.info(f"Starting optimized Kafka consumer for partitions: {self.partition_ids}")
        
        # 启动定时刷新任务
        flush_task = asyncio.create_task(self._periodic_flush_task())
        
        try:
            while self.running:
                try:
                    # 消费消息并累积到缓冲区
                    messages_fetched = await self._fetch_and_buffer_messages()
                    
                    # 检查是否达到批处理大小阈值（立即触发）
                    if len(self.user_events_buffer) >= self.max_batch_size:
                        await self._flush_user_batch("size_triggered")
                    elif not messages_fetched:
                        # 没有新消息时短暂休眠
                        await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.error(f"Error in message consumption: {e}")
                    await asyncio.sleep(1)  # 错误时短暂休眠
        finally:
            # 取消定时任务
            flush_task.cancel()
            try:
                await flush_task
            except asyncio.CancelledError:
                pass
            
            # 刷新剩余数据
            if self.user_events_buffer:
                await self._flush_user_batch("shutdown")
    
    async def _periodic_flush_task(self):
        """定期刷新任务 - 独立的协程处理时间触发"""
        while self.running:
            try:
                # 等待批处理超时时间
                await asyncio.sleep(self.batch_timeout_seconds)
                
                # 检查是否有待处理的用户事件且超过时间阈值
                if (self.user_events_buffer and 
                    time.time() - self.last_batch_time >= self.batch_timeout_seconds):
                    await self._flush_user_batch("time_triggered")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush task: {e}")
                await asyncio.sleep(1)
    
    async def _fetch_and_buffer_messages(self) -> bool:
        """获取消息并缓冲到用户事件字典中"""
        messages_fetched = 0
        fetch_timeout = 0.5  # 500ms获取超时
        
        # 尝试获取一定数量的消息
        for _ in range(50):  # 每次最多获取50条消息
            msg = self.consumer.poll(timeout=fetch_timeout)
            
            if msg is None:
                break  # 没有更多消息
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"Reached end of partition {msg.partition()}")
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    self.stats['errors'] += 1
                    continue
            
            # 解析消息
            parsed_event = self._parse_cdc_message(msg)
            if parsed_event and parsed_event.get('user_id'):
                user_id = parsed_event['user_id']
                
                # 用户去重：只保留每个用户的最新事件
                # 如果已存在该用户的事件，比较时间戳，保留最新的
                if user_id in self.user_events_buffer:
                    existing_event = self.user_events_buffer[user_id]
                    if self._is_newer_event(parsed_event, existing_event):
                        self.user_events_buffer[user_id] = parsed_event
                else:
                    self.user_events_buffer[user_id] = parsed_event
                
                messages_fetched += 1
                self.stats['messages_consumed'] += 1
                self.stats['last_offset'][msg.partition()] = msg.offset()
        
        return messages_fetched > 0
    
    def _is_newer_event(self, new_event: Dict, existing_event: Dict) -> bool:
        """判断新事件是否比现有事件更新"""
        new_timestamp = new_event.get('timestamp')
        existing_timestamp = existing_event.get('timestamp')
        
        # 如果没有时间戳，比较offset
        if not new_timestamp or not existing_timestamp:
            return new_event.get('offset', 0) > existing_event.get('offset', 0)
        
        # 比较时间戳
        try:
            # 假设时间戳是ISO格式字符串
            from datetime import datetime
            new_dt = datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))
            existing_dt = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))
            return new_dt > existing_dt
        except:
            # 时间戳解析失败时，比较offset
            return new_event.get('offset', 0) > existing_event.get('offset', 0)
    
    async def _flush_user_batch(self, trigger_reason: str = "unknown"):
        """刷新用户事件批次到BufferManager"""
        # 检查缓冲区是否为空，为空则直接返回
        if not self.user_events_buffer:
            self.stats['empty_flush_skipped'] += 1
            logger.debug(f"Skipping {trigger_reason} flush - buffer is empty (total skipped: {self.stats['empty_flush_skipped']})")
            return
        
        # 构建要发送的事件列表（每个用户一个事件）
        unique_user_events = list(self.user_events_buffer.values())
        unique_user_count = len(unique_user_events)
        
        logger.debug(f"Starting {trigger_reason} flush with {unique_user_count} unique users")
        
        try:
            # 使用ActorPool分发任务到BufferManager
            self.manager_pool.submit(
                lambda actor, events: actor.process_event_batch.remote(events),
                unique_user_events
            )
            
            # 更新统计信息
            self.stats['batches_sent'] += 1
            self.stats['unique_users_processed'] += unique_user_count
            
            if trigger_reason == "time_triggered":
                self.stats['time_triggered_batches'] += 1
                logger.info(f"Time-triggered batch sent: {unique_user_count} unique users")
            elif trigger_reason == "size_triggered":
                self.stats['size_triggered_batches'] += 1
                logger.info(f"Size-triggered batch sent: {unique_user_count} unique users")
            else:
                logger.info(f"{trigger_reason} batch sent: {unique_user_count} unique users")
            
        except Exception as e:
            logger.error(f"Error submitting {trigger_reason} batch to actor pool: {e}")
            self.stats['errors'] += 1
        
        finally:
            # 清空缓冲区并更新时间
            self.user_events_buffer.clear()
            self.last_batch_time = time.time()
    
    def _parse_cdc_message(self, msg) -> Optional[Dict]:
        """
        解析CDC消息，提取用户事件信息
        
        Args:
            msg: Confluent Kafka消息对象
            
        Returns:
            解析后的事件信息或None
        """
        try:
            # 获取消息值并解析JSON
            message_value = msg.value()
            if message_value is None:
                return None
                
            # confluent_kafka返回bytes，需要解码
            if isinstance(message_value, bytes):
                message_str = message_value.decode('utf-8')
            else:
                message_str = str(message_value)
                
            message = json.loads(message_str)
            
            # 解析CDC消息结构
            after_data = message.get('after', {})
            if not after_data:
                return None
                
            # 提取关键信息
            user_id = after_data.get('user_id')
            if not user_id:
                return None
            
            return {
                'user_id': user_id,
                'operation': message.get('op'),
                'timestamp': after_data.get('updated_at'),
                'partition': msg.partition(),
                'offset': msg.offset(),
                'table_name': message.get('source', {}).get('table', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to parse CDC message: {e}")
            return None
    
    async def stop_consuming(self):
        """停止消费并刷新剩余缓冲区数据"""
        self.running = False
        
        # 刷新剩余的用户事件
        if self.user_events_buffer:
            logger.info(f"Flushing {len(self.user_events_buffer)} remaining user events before shutdown")
            await self._flush_user_batch("shutdown")
        
        if self.consumer:
            self.consumer.close()
        logger.info(f"Kafka consumer stopped for partitions: {self.partition_ids}")
    
    async def force_flush(self):
        """强制刷新当前缓冲区（用于调试或手动触发）"""
        if self.user_events_buffer:
            buffer_size = len(self.user_events_buffer)
            logger.info(f"Force flushing {buffer_size} user events")
            await self._flush_user_batch("manual_flush")
            return buffer_size
        return 0
    
    async def get_stats(self) -> Dict:
        """获取消费统计信息"""
        current_time = time.time()
        stats = self.stats.copy()
        
        # 添加实时统计信息
        stats.update({
            'current_buffer_size': len(self.user_events_buffer),
            'seconds_since_last_batch': current_time - self.last_batch_time if self.last_batch_time else 0,
            'deduplication_ratio': (stats['unique_users_processed'] / stats['messages_consumed']) 
                                  if stats['messages_consumed'] > 0 else 0,
        })
        
        return stats
    
    async def health_check(self) -> Dict:
        """健康检查"""
        try:
            # 检查消费者连接状态
            if not self.consumer:
                return {'status': 'unhealthy', 'reason': 'consumer_not_initialized'}
            
            # 检查分区分配
            assignment = self.consumer.assignment()
            if not assignment:
                return {'status': 'unhealthy', 'reason': 'no_partitions_assigned'}
            
            return {
                'status': 'healthy',
                'partitions': [p.partition for p in assignment],
                'stats': self.stats
            }
            
        except Exception as e:
            return {'status': 'unhealthy', 'reason': str(e)}