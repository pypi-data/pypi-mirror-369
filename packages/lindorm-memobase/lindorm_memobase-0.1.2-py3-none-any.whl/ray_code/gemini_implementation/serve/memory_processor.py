import logging
import time
from typing import List, Dict, Any
from ray import serve

# 导入lindorm-memobase
from lindormmemobase import LindormMemobase
from lindormmemobase.models.blob import BlobType
from lindormmemobase.config import Config

# 导入配置管理器
from utils.config_manager import config_manager

logger = logging.getLogger(__name__)


@serve.deployment(
    name="MemoryProcessor",
    autoscaling_config={
        "min_replicas": 10,              # 最小副本数，保证基础处理能力
        "max_replicas": 100,             # 最大副本数，根据实际资源调整
        "target_num_ongoing_requests_per_replica": 10,  # 每个副本的目标并发请求数
        "look_back_period_s": 30,        # 监控周期
        "smoothing_factor": 1.0,         # 平滑因子，控制扩缩容速度
    },
    # 声明式资源配置
    ray_actor_options={
        "num_cpus": 2,                   # 每个副本的CPU资源
        "num_gpus": 0,                   # 不使用GPU（LLM API调用模式）
        "memory": 1 * 1024 * 1024 * 1024  # 1GB内存
    },
    # 健康检查配置
    health_check_period_s=30,
    health_check_timeout_s=60
)
class MemoryProcessorDeployment:
    """
    基于Ray Serve的记忆处理器 - Gemini方案核心组件
    
    特点：
    - 由Ray Serve自动管理生命周期、伸缩和负载均衡
    - 声明式配置，无需手动管理并发控制
    - 内置健康检查和故障恢复
    - 专注业务逻辑，基础设施由Ray Serve处理
    """
    
    def __init__(self):
        """初始化MemoryProcessor"""
        # 使用配置管理器加载config.yaml配置
        memobase_config = config_manager.load_memobase_config()
        self.memobase = LindormMemobase(config=memobase_config)
        self.start_time = time.time()
        
        logger.info("MemoryProcessor initialized with config.yaml configuration")
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0,
            'avg_processing_time': 0
        }
        
        logger.info("MemoryProcessor deployment initialized")
    
    async def process(self, user_id: str, blob_ids: List[str]) -> Dict[str, Any]:
        """
        处理单个用户的记忆抽取请求
        
        Args:
            user_id: 用户ID
            blob_ids: 需要处理的blob ID列表
            
        Returns:
            处理结果
        """
        start_time = time.time()
        request_id = f"{user_id}_{int(start_time * 1000)}"
        
        logger.info(f"Processing memory extraction for user {user_id}, "
                   f"blob_count: {len(blob_ids)}, request_id: {request_id}")
        
        try:
            # 更新统计 - 请求开始
            self.stats['total_requests'] += 1
            
            # 调用核心业务逻辑
            # Ray Serve会自动控制此方法的并发调用数，无需手动管理
            result = await self.memobase.process_buffer(
                user_id=user_id,
                blob_type=BlobType.chat,  # 指定为聊天类型
                blob_ids=blob_ids
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 更新统计 - 成功
            self.stats['successful_requests'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['avg_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['successful_requests']
            )
            
            logger.info(f"Successfully processed user {user_id} in {processing_time:.2f}s, "
                       f"request_id: {request_id}")
            
            return {
                'success': True,
                'user_id': user_id,
                'request_id': request_id,
                'result': result,
                'processing_time': processing_time,
                'timestamp': time.time()
            }
            
        except Exception as e:
            # 处理异常
            processing_time = time.time() - start_time
            self.stats['failed_requests'] += 1
            
            logger.error(f"Failed to process user {user_id}: {e}, "
                        f"request_id: {request_id}, time: {processing_time:.2f}s")
            
            # Ray Serve会自动记录异常并处理重试逻辑
            return {
                'success': False,
                'user_id': user_id,
                'request_id': request_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'processing_time': processing_time,
                'timestamp': time.time()
            }
    
    async def batch_process(self, requests: List[Dict]) -> List[Dict]:
        """
        批量处理多个用户请求（可选功能）
        
        Args:
            requests: 包含user_id和blob_ids的请求列表
            
        Returns:
            处理结果列表
        """
        logger.info(f"Batch processing {len(requests)} requests")
        
        # 并发处理所有请求
        import asyncio
        tasks = [
            self.process(req['user_id'], req['blob_ids']) 
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'user_id': requests[i]['user_id'],
                    'error': str(result),
                    'error_type': type(result).__name__
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取处理器统计信息"""
        uptime = time.time() - self.start_time
        
        return {
            'deployment_name': 'MemoryProcessor',
            'uptime_seconds': uptime,
            'stats': self.stats.copy(),
            'requests_per_second': self.stats['total_requests'] / uptime if uptime > 0 else 0,
            'success_rate': (
                self.stats['successful_requests'] / self.stats['total_requests'] 
                if self.stats['total_requests'] > 0 else 0
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查端点"""
        try:
            # 检查memobase连接 - 使用一个轻量级的检测
            # 执行缓冲区状态检查作为健康检查
            await self.memobase.detect_buffer_full_or_not("health_check_user", BlobType.chat)
            memobase_healthy = True
        except Exception:
            memobase_healthy = False
        
        # 检查基本统计
        recent_error_rate = 0
        if self.stats['total_requests'] > 0:
            recent_error_rate = self.stats['failed_requests'] / self.stats['total_requests']
        
        is_healthy = memobase_healthy and recent_error_rate < 0.1  # 错误率低于10%
        
        return {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'memobase_connection': memobase_healthy,
            'error_rate': recent_error_rate,
            'uptime': time.time() - self.start_time,
            'total_requests': self.stats['total_requests']
        }
        

# 可选：创建简化的部署函数
def create_memory_processor_deployment():
    """创建并返回MemoryProcessor部署"""
    return MemoryProcessorDeployment.bind()


# 可选：用于测试的简单HTTP端点
@serve.deployment(name="MemoryProcessorAPI")
class MemoryProcessorAPI:
    """
    为MemoryProcessor提供HTTP API接口（可选）
    主要用于监控和调试
    """
    
    def __init__(self):
        self.processor_handle = serve.get_deployment("MemoryProcessor").get_handle()
    
    async def __call__(self, request):
        """处理HTTP请求"""
        import json
        from starlette.responses import JSONResponse
        
        if request.method == "POST":
            try:
                body = await request.json()
                user_id = body.get('user_id')
                blob_ids = body.get('blob_ids', [])
                
                if not user_id:
                    return JSONResponse(
                        {'error': 'user_id is required'}, 
                        status_code=400
                    )
                
                # 调用处理器
                result = await self.processor_handle.process.remote(user_id, blob_ids)
                return JSONResponse(result)
                
            except Exception as e:
                return JSONResponse(
                    {'error': str(e)}, 
                    status_code=500
                )
        
        elif request.method == "GET":
            # 返回统计信息
            stats = await self.processor_handle.get_stats.remote()
            return JSONResponse(stats)
        
        else:
            return JSONResponse(
                {'error': 'Method not allowed'}, 
                status_code=405
            )