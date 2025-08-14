"""
Ray Gemini方案长期记忆系统主启动文件

基于Gemini优化方案的实现，特点：
1. 声明式配置优于命令式编程
2. 使用Ray Serve自动伸缩
3. 去中心化架构，使用ActorPool管理
4. 最小化自定义基础设施代码
5. 统一使用LindormMemobase.from_yaml_file加载配置
"""

import ray
import asyncio
import logging
import signal
import sys
import os
from ray import serve
from ray.util import ActorPool
from typing import List, Optional

# 导入LindormMemobase
from lindormmemobase import LindormMemobase

# 导入项目组件
from actors.kafka_consumer import KafkaConsumerActor
from actors.buffer_manager import BufferManagerActor
from serve.memory_processor import MemoryProcessorDeployment, MemoryProcessorAPI
from utils.helpers import HealthChecker, metrics_collector
from utils.config_manager import get_system_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LongTermMemorySystem:
    """
    基于Gemini方案的长期记忆系统主类
    """
    def __init__(self, config_file_path: str = "./config.yaml"):
        """
        初始化长期记忆系统
        
        Args:
            config_file_path: LindormMemobase配置文件路径
        """
        self.config_file_path = config_file_path
        self.kafka_consumers: List[KafkaConsumerActor] = []
        self.buffer_manager_pool: Optional[ActorPool] = None
        self.running = False
        
        # 初始化LindormMemobase实例
        try:
            logger.info(f"Loading LindormMemobase config from: {config_file_path}")
            self.memobase = LindormMemobase.from_yaml_file(config_file_path)
            logger.info("LindormMemobase initialized successfully from config file")
        except Exception as e:
            logger.error(f"Failed to initialize LindormMemobase: {e}")
            raise
        
        # 从环境变量获取系统配置参数
        system_config = get_system_config()
        self.num_kafka_consumers = system_config.get('num_kafka_consumers', 4)
        self.num_buffer_managers = system_config.get('num_buffer_managers', 10)
        self.kafka_partitions = system_config.get('kafka_partitions', list(range(8)))
        self.kafka_batch_timeout_seconds = system_config.get('kafka_batch_timeout_seconds', 10)
        self.kafka_max_batch_size = system_config.get('kafka_max_batch_size', 100)
        self.enable_http_api = system_config.get('enable_http_api', True)
    
    async def initialize(self):
        """初始化系统组件"""
        logger.info("Initializing Long Term Memory System...")
        
        try:
            # 1. 初始化Ray（如果尚未初始化）
            if not ray.is_initialized():
                ray.init(address='auto')  # 连接到现有集群或启动本地集群
                logger.info("Ray initialized")
            
            # 2. 启动Ray Serve并部署MemoryProcessor
            await self._deploy_memory_processor()
            
            # 3. 创建BufferManager Actor池
            await self._create_buffer_manager_pool()
            
            # 4. 创建Kafka Consumer Actors
            await self._create_kafka_consumers()
            
            # 5. 系统健康检查
            await self._system_health_check()
            
            logger.info("Long Term Memory System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    async def _deploy_memory_processor(self):
        """部署Ray Serve MemoryProcessor"""
        logger.info("Deploying MemoryProcessor service...")
        
        # 启动Ray Serve
        serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8000})
        
        # 部署MemoryProcessor，传递memobase实例
        memory_processor = MemoryProcessorDeployment.bind(memobase_config_path=self.config_file_path)
        serve.run(memory_processor, name="MemoryProcessor", route_prefix="/memory")
        
        # 可选：部署HTTP API
        if self.enable_http_api:
            api = MemoryProcessorAPI.bind(memobase_config_path=self.config_file_path)
            serve.run(api, name="MemoryProcessorAPI", route_prefix="/api")
            logger.info("MemoryProcessor HTTP API deployed at /api")
        
        logger.info("MemoryProcessor service deployed successfully")
    
    async def _create_buffer_manager_pool(self):
        """创建BufferManager Actor池"""
        logger.info(f"Creating BufferManager pool with {self.num_buffer_managers} actors...")
        
        # 创建BufferManager actors，传递配置文件路径
        buffer_managers = [
            BufferManagerActor.remote(
                manager_id=i, 
                memobase_config_path=self.config_file_path
            )
            for i in range(self.num_buffer_managers)
        ]
        
        # 等待所有actors初始化完成
        await asyncio.gather(*[
            actor.__ray_ready__.remote() for actor in buffer_managers
        ])
        
        # 创建ActorPool
        self.buffer_manager_pool = ActorPool(buffer_managers)
        
        logger.info(f"BufferManager pool created with {self.num_buffer_managers} actors")
    
    async def _create_kafka_consumers(self):
        """创建Kafka Consumer Actors"""
        logger.info(f"Creating {self.num_kafka_consumers} Kafka consumers...")
        
        # 从环境变量获取Kafka配置
        from utils.config_manager import get_kafka_config
        kafka_config = get_kafka_config()
        
        # 将分区分配给不同的消费者
        partitions_per_consumer = len(self.kafka_partitions) // self.num_kafka_consumers
        
        for i in range(self.num_kafka_consumers):
            start_idx = i * partitions_per_consumer
            end_idx = start_idx + partitions_per_consumer if i < self.num_kafka_consumers - 1 else len(self.kafka_partitions)
            assigned_partitions = self.kafka_partitions[start_idx:end_idx]
            
            consumer = KafkaConsumerActor.remote(
                partition_ids=assigned_partitions,
                buffer_manager_pool=self.buffer_manager_pool,
                kafka_config=kafka_config,
                batch_timeout_seconds=self.kafka_batch_timeout_seconds,
                max_batch_size=self.kafka_max_batch_size
            )
            
            self.kafka_consumers.append(consumer)
            
            logger.info(f"Kafka consumer {i} assigned partitions: {assigned_partitions}")
        
        logger.info(f"Created {len(self.kafka_consumers)} Kafka consumers")
    
    async def _system_health_check(self):
        """系统健康检查"""
        logger.info("Performing system health check...")
        
        # 检查Ray集群状态
        cluster_resources = ray.cluster_resources()
        logger.info(f"Ray cluster resources: {cluster_resources}")
        
        # 检查Kafka连接
        from utils.config_manager import get_kafka_config
        kafka_config = get_kafka_config()
        kafka_healthy = await HealthChecker.check_kafka_connection(kafka_config)
        logger.info(f"Kafka connection: {'healthy' if kafka_healthy else 'unhealthy'}")
        
        # 检查LindormMemobase连接（通过测试一个简单操作）
        lindorm_healthy = True
        try:
            # 尝试获取一个测试用户的buffer状态来验证连接
            await self.memobase.detect_buffer_full_or_not("health_check_user")
            logger.info("LindormMemobase connection: healthy")
        except Exception as e:
            logger.error(f"LindormMemobase connection test failed: {e}")
            lindorm_healthy = False
            logger.info("LindormMemobase connection: unhealthy")
        
        # 检查Ray Serve状态
        try:
            deployments = serve.list_deployments()
            logger.info(f"Ray Serve deployments: {list(deployments.keys())}")
        except Exception as e:
            logger.error(f"Failed to check Ray Serve status: {e}")
        
        if not (kafka_healthy and lindorm_healthy):
            raise RuntimeError("System health check failed")
        
        logger.info("System health check passed")
    
    async def start(self):
        """启动系统"""
        logger.info("Starting Long Term Memory System...")
        
        self.running = True
        
        # 启动所有Kafka消费者
        consumer_tasks = [
            consumer.start_consuming.remote() 
            for consumer in self.kafka_consumers
        ]
        
        logger.info("All Kafka consumers started")
        
        # 启动监控任务
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        try:
            # 等待所有任务完成（通常不会自然结束）
            await asyncio.gather(*consumer_tasks, monitoring_task)
        except asyncio.CancelledError:
            logger.info("System shutdown requested")
        except Exception as e:
            logger.error(f"System error: {e}")
            raise
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 收集系统统计信息
                await self._collect_system_stats()
                
                # 等待下一次监控周期
                await asyncio.sleep(30)  # 每30秒监控一次
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)  # 错误时减少监控频率
    
    async def _collect_system_stats(self):
        """收集系统统计信息"""
        try:
            # 收集Kafka消费者统计
            consumer_stats = await asyncio.gather(*[
                consumer.get_stats.remote() for consumer in self.kafka_consumers
            ], return_exceptions=True)
            
            # 收集BufferManager统计
            # 注意：ActorPool不直接支持批量调用，这里简化处理
            
            # 记录到指标收集器
            total_messages = sum(
                stats.get('messages_consumed', 0) 
                for stats in consumer_stats 
                if isinstance(stats, dict)
            )
            
            metrics_collector.set_gauge('total_messages_consumed', total_messages)
            metrics_collector.set_gauge('active_consumers', len(self.kafka_consumers))
            
            # 获取Ray集群资源使用情况
            cluster_resources = ray.cluster_resources()
            available_resources = ray.available_resources()
            
            cpu_usage = 1 - (available_resources.get('CPU', 0) / cluster_resources.get('CPU', 1))
            metrics_collector.set_gauge('cluster_cpu_usage', cpu_usage)
            
            logger.debug(f"System stats: messages={total_messages}, cpu_usage={cpu_usage:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to collect system stats: {e}")
    
    async def stop(self):
        """停止系统"""
        logger.info("Stopping Long Term Memory System...")
        
        self.running = False
        
        # 停止Kafka消费者
        stop_tasks = [
            consumer.stop_consuming.remote() 
            for consumer in self.kafka_consumers
        ]
        
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # 停止Ray Serve
        serve.shutdown()
        
        logger.info("Long Term Memory System stopped")


async def main():
    """主函数"""
    # 检查配置文件是否存在
    config_file_path = "./config.yaml"
    if not os.path.exists(config_file_path):
        logger.error(f"Configuration file not found: {config_file_path}")
        logger.error("Please ensure config.yaml exists in the current directory")
        sys.exit(1)
    
    logger.info(f"Using configuration file: {config_file_path}")
    
    # 创建系统实例
    system = LongTermMemorySystem(config_file_path=config_file_path)
    
    # 设置信号处理
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(system.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 初始化并启动系统
        await system.initialize()
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise
    finally:
        await system.stop()


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())