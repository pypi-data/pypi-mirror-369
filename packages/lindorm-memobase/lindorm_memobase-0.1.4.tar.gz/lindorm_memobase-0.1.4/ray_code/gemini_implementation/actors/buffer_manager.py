import ray
import asyncio
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from ray import serve

# 导入lindorm-memobase
from lindormmemobase import LindormMemobase
from lindormmemobase.models.blob import BlobType

logger = logging.getLogger(__name__)


@ray.remote
class BufferManagerActor:
    """
    缓冲区管理Actor，基于Gemini方案设计
    - 由ActorPool管理，负责检查用户缓冲区状态
    - 使用线程池处理数据库IO，避免阻塞
    - 直接调用Ray Serve进行下游处理，无需中心化管理器
    """
    
    def __init__(self, manager_id: int, memobase_config_path: str = "./config.yaml", db_config: Optional[Dict] = None):
        """
        初始化BufferManager
        
        Args:
            manager_id: 管理器ID
            memobase_config_path: LindormMemobase配置文件路径
            db_config: 数据库配置（已弃用，保留以保持兼容性）
        """
        self.manager_id = manager_id
        self.memobase_config_path = memobase_config_path
        self.db_config = db_config or {}  # 保留以防代码中有引用
        
        # 初始化线程池用于数据库IO
        self.db_thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # 初始化Lindorm Memobase连接
        try:
            # 直接使用LindormMemobase.from_yaml_file加载配置
            logger.info(f"BufferManager {manager_id} loading config from: {memobase_config_path}")
            self.memobase = LindormMemobase.from_yaml_file(memobase_config_path)
            logger.info(f"BufferManager {manager_id} initialized with LindormMemobase using config file")
        except Exception as e:
            logger.error(f"Failed to initialize LindormMemobase: {e}")
            raise
        
        # 获取Ray Serve部署句柄 - 延迟初始化
        self.processor_handle = None
        self._serve_handle_retry_count = 0
        self._max_retry_attempts = 5
        
        # 统计信息
        self.stats = {
            'events_processed': 0,
            'buffer_checks': 0,
            'full_buffers_found': 0,
            'processing_requests_sent': 0,
            'errors': 0
        }
    
    async def _get_serve_handle_with_retry(self):
        """
        获取Ray Serve句柄，带重试机制
        
        Returns:
            bool: 是否成功获取句柄
        """
        if self.processor_handle:
            return True
            
        if self._serve_handle_retry_count >= self._max_retry_attempts:
            logger.error(f"BufferManager {self.manager_id} exceeded max retry attempts for Ray Serve handle")
            return False
            
        try:
            # 尝试获取句柄
            self.processor_handle = serve.get_deployment("MemoryProcessor").get_handle()
            logger.info(f"BufferManager {self.manager_id} successfully connected to MemoryProcessor service")
            self._serve_handle_retry_count = 0  # 重置重试计数
            return True
            
        except Exception as e:
            self._serve_handle_retry_count += 1
            logger.warning(f"BufferManager {self.manager_id} failed to get Ray Serve handle "
                          f"(attempt {self._serve_handle_retry_count}/{self._max_retry_attempts}): {e}")
            
            # 指数退避延迟
            if self._serve_handle_retry_count < self._max_retry_attempts:
                delay = min(2 ** self._serve_handle_retry_count, 30)  # 最大30秒
                logger.info(f"BufferManager {self.manager_id} will retry in {delay} seconds")
                await asyncio.sleep(delay)
                
            return False
    
    def _init_serve_handle(self):
        """初始化Ray Serve句柄 - 已弃用，保留以兼容现有代码"""
        # 这个方法现在什么都不做，实际获取在 _get_serve_handle_with_retry 中进行
        pass

    async def process_event_batch(self, events: List[Dict]) -> Dict:
        """
        处理一批用户事件
        
        Args:
            events: 用户事件列表
            
        Returns:
            处理结果统计
        """
        if not events:
            return {'processed': 0, 'triggered': 0}
        
        # 去重 - 同一批次中相同用户只处理一次
        unique_users = {}
        for event in events:
            user_id = event.get('user_id')
            if user_id:
                unique_users[user_id] = event
        
        logger.debug(f"BufferManager {self.manager_id} processing {len(unique_users)} unique users")
        
        # 并发检查所有用户
        tasks = [self._check_and_trigger_user(user_id, event) 
                for user_id, event in unique_users.items()]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        processed = len(results)
        triggered = sum(1 for r in results if isinstance(r, dict) and r.get('triggered', False))
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        # 更新统计
        self.stats['events_processed'] += len(events)
        self.stats['buffer_checks'] += processed
        self.stats['processing_requests_sent'] += triggered
        self.stats['errors'] += errors
        
        return {
            'processed': processed,
            'triggered': triggered,
            'errors': errors,
            'manager_id': self.manager_id
        }
    
    async def _check_and_trigger_user(self, user_id: str, event: Dict) -> Dict:
        """
        检查单个用户缓冲区并触发处理
        
        Args:
            user_id: 用户ID
            event: 原始事件信息
            
        Returns:
            处理结果
        """
        try:
            # 直接异步调用缓冲区检测方法
            status = await self.memobase.detect_buffer_full_or_not(user_id, BlobType.chat)
            
            if status.get('is_full', False):
                buffer_ids = status.get('buffer_full_ids', [])
                logger.info(f"Buffer full for user {user_id}, triggering memory processing")
                
                # 获取Ray Serve句柄（带重试机制）
                handle_ready = await self._get_serve_handle_with_retry()
                
                if handle_ready and self.processor_handle:
                    # 异步提交到Ray Serve，不等待结果
                    self.processor_handle.process.remote(user_id, buffer_ids)
                    
                    self.stats['full_buffers_found'] += 1
                    return {
                        'user_id': user_id,
                        'triggered': True,
                        'buffer_ids_count': len(buffer_ids)
                    }
                else:
                    logger.error(f"BufferManager {self.manager_id} MemoryProcessor service not available for user {user_id}")
                    return {
                        'user_id': user_id,
                        'triggered': False,
                        'error': 'service_unavailable'
                    }
            else:
                return {
                    'user_id': user_id,
                    'triggered': False,
                    'reason': 'buffer_not_full'
                }
                
        except Exception as e:
            logger.error(f"Error checking buffer for user {user_id}: {e}")
            return {
                'user_id': user_id,
                'triggered': False,
                'error': str(e)
            }
    
    async def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'manager_id': self.manager_id,
            'stats': self.stats.copy(),
            'thread_pool_size': self.db_thread_pool._max_workers,
            'processor_handle_ready': self.processor_handle is not None,
            'serve_retry_count': self._serve_handle_retry_count,
            'max_retry_attempts': self._max_retry_attempts
        }
    
    async def health_check(self) -> Dict:
        """健康检查"""
        try:
            # 检查数据库连接
            test_result = await self._test_db_connection()
            
            # 检查Ray Serve连接 - 尝试获取句柄而不是仅检查是否存在
            serve_handle_ready = await self._get_serve_handle_with_retry()
            
            return {
                'manager_id': self.manager_id,
                'status': 'healthy' if test_result and serve_handle_ready else 'degraded',
                'database_connection': test_result,
                'serve_connection': serve_handle_ready,
                'serve_retry_count': self._serve_handle_retry_count,
                'stats': self.stats
            }
            
        except Exception as e:
            return {
                'manager_id': self.manager_id,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _test_db_connection(self) -> bool:
        """测试LindormMemobase连接"""
        try:
            # 执行一个简单的检测来测试连接
            # 使用一个测试用户ID，这个调用会验证连接是否正常
            await self.memobase.detect_buffer_full_or_not("health_check_user", BlobType.chat)
            return True
        except Exception as e:
            logger.error(f"LindormMemobase connection test failed: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        if self.db_thread_pool:
            self.db_thread_pool.shutdown(wait=True)
        logger.info(f"BufferManager {self.manager_id} cleaned up")