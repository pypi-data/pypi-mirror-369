import logging
import asyncio
import os
from typing import Dict, List

# 导入配置管理器
from .config_manager import get_kafka_config, get_database_config, get_system_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def validate_user_id(user_id: str) -> bool:
    """
    验证用户ID格式
    
    Args:
        user_id: 用户ID
        
    Returns:
        是否有效
    """
    if not user_id or not isinstance(user_id, str):
        return False
    
    # 添加具体的验证逻辑
    if len(user_id) < 1 or len(user_id) > 100:
        return False
        
    return True


def batch_events_by_user(events: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按用户ID对事件进行分组
    
    Args:
        events: 事件列表
        
    Returns:
        按用户分组的事件字典
    """
    user_events = {}
    
    for event in events:
        user_id = event.get('user_id')
        if user_id and validate_user_id(user_id):
            if user_id not in user_events:
                user_events[user_id] = []
            user_events[user_id].append(event)
    
    return user_events


async def retry_with_backoff(coro, max_retries: int = 3, base_delay: float = 1.0):
    """
    带指数退避的重试机制
    
    Args:
        coro: 协程函数
        max_retries: 最大重试次数
        base_delay: 基础延迟时间
        
    Returns:
        协程执行结果
    """
    for attempt in range(max_retries + 1):
        try:
            return await coro()
        except Exception as e:
            if attempt == max_retries:
                raise e
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
            await asyncio.sleep(delay)


# 注意：这些函数现在从config_manager模块导入
# 保留原有接口兼容性


# 数据库配置函数现在也从config_manager模块导入


class HealthChecker:
    """通用健康检查器"""
    
    @staticmethod
    async def check_kafka_connection(kafka_config: Dict) -> bool:
        """检查Kafka连接"""
        try:
            from confluent_kafka import Consumer
            
            # 创建临时消费者测试连接
            test_config = {
                'bootstrap.servers': ','.join(kafka_config.get('bootstrap_servers', ['localhost:9092'])),
                'group.id': 'health_check_group',
                'auto.offset.reset': 'latest',
                'enable.auto.commit': False,
                'session.timeout.ms': 6000,
                'api.version.request': True
            }
            
            consumer = Consumer(test_config)
            
            # 尝试获取元数据来测试连接
            metadata = consumer.list_topics(timeout=5.0)
            consumer.close()
            
            return len(metadata.topics) >= 0  # 如果能获取到topics信息说明连接正常
            
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return False
    
    @staticmethod
    async def check_database_connection(db_config: Dict) -> bool:
        """检查数据库连接"""
        try:
            # 这里应该实现实际的数据库连接检查
            # 暂时返回True
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, metric_name: str, value: int = 1):
        """增加计数器指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = 0
        self.metrics[metric_name] += value
    
    def set_gauge(self, metric_name: str, value: float):
        """设置量表指标"""
        self.metrics[metric_name] = value
    
    def get_metrics(self) -> Dict:
        """获取所有指标"""
        return self.metrics.copy()
    
    def reset(self):
        """重置所有指标"""
        self.metrics.clear()


# 全局指标收集器实例
metrics_collector = MetricsCollector()