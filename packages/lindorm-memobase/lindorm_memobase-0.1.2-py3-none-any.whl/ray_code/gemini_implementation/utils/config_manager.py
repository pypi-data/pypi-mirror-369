"""
配置管理工具类
用于在Ray环境中加载和管理LindormMemobase配置
"""

import os
import yaml
import logging
from typing import Dict, Optional
from pathlib import Path
from lindormmemobase.config import Config

logger = logging.getLogger(__name__)


class ConfigManager:
    """统一配置管理器，支持环境变量、YAML文件和默认值"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: 配置文件路径，默认为 'config.yaml'
        """
        self.config_file_path = config_file_path or "config.yaml"
        self._config = None
        self._raw_config_dict = None
    
    def load_memobase_config(self) -> Config:
        """
        加载LindormMemobase配置
        
        Returns:
            Config: LindormMemobase配置对象
        """
        if self._config is not None:
            return self._config
            
        try:
            # 检查配置文件是否存在
            if os.path.exists(self.config_file_path):
                logger.info(f"Loading LindormMemobase config from {self.config_file_path}")
                self._config = Config.from_yaml_file(self.config_file_path)
            else:
                logger.warning(f"Config file {self.config_file_path} not found, using environment variables and defaults")
                self._config = Config.load_config()
            
            logger.info("LindormMemobase configuration loaded successfully")
            return self._config
            
        except Exception as e:
            logger.error(f"Failed to load LindormMemobase config: {e}")
            raise
    
    def get_raw_config_dict(self) -> Dict:
        """
        获取原始配置字典（用于传递给Ray环境）
        
        Returns:
            Dict: 原始配置字典
        """
        if self._raw_config_dict is not None:
            return self._raw_config_dict
            
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    self._raw_config_dict = yaml.safe_load(f) or {}
            else:
                self._raw_config_dict = {}
                
            return self._raw_config_dict
            
        except Exception as e:
            logger.error(f"Failed to load raw config dict: {e}")
            return {}
    
    def get_kafka_config(self) -> Dict:
        """
        从环境变量获取Kafka配置
        
        Returns:
            Dict: Kafka配置
        """
        return {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
            'topics': [os.getenv('KAFKA_TOPIC', 'buffer_zone_cdc')],
            'consumer_group': os.getenv('KAFKA_CONSUMER_GROUP', 'memory_processing_group')
        }
    
    def get_database_config(self) -> Dict:
        """
        从环境变量获取数据库配置
        
        Returns:
            Dict: 数据库配置
        """
        return {
            'connection_string': os.getenv('DATABASE_CONNECTION', 'mysql://root:password@localhost:3306/memory_db')
        }
    
    def get_system_config(self) -> Dict:
        """
        从环境变量获取系统配置
        
        Returns:
            Dict: 系统配置
        """
        return {
            'num_kafka_consumers': int(os.getenv('NUM_KAFKA_CONSUMERS', '4')),
            'num_buffer_managers': int(os.getenv('NUM_BUFFER_MANAGERS', '10')),
            'kafka_partitions': list(range(int(os.getenv('KAFKA_PARTITIONS', '8')))),
            'enable_http_api': os.getenv('ENABLE_HTTP_API', 'true').lower() == 'true',
            'kafka_batch_timeout_seconds': int(os.getenv('KAFKA_BATCH_TIMEOUT_SECONDS', '10')),
            'kafka_max_batch_size': int(os.getenv('KAFKA_MAX_BATCH_SIZE', '100')),
            'enable_monitoring': os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
        }
    
    def generate_env_vars_for_ray(self) -> Dict[str, str]:
        """
        生成用于Ray环境的环境变量字典
        将config.yaml中的配置转换为环境变量格式
        
        Returns:
            Dict[str, str]: 环境变量字典
        """
        env_vars = {}
        raw_config = self.get_raw_config_dict()
        
        # 将配置项转换为MEMOBASE_*环境变量
        for key, value in raw_config.items():
            if value is not None:
                env_var_name = f"MEMOBASE_{key.upper()}"
                
                # 处理不同类型的值
                if isinstance(value, (dict, list)):
                    import json
                    env_vars[env_var_name] = json.dumps(value)
                elif isinstance(value, bool):
                    env_vars[env_var_name] = str(value).lower()
                else:
                    env_vars[env_var_name] = str(value)
        
        logger.info(f"Generated {len(env_vars)} environment variables for Ray deployment")
        return env_vars
    
    @staticmethod
    def create_default_config_file(file_path: str = "config.yaml"):
        """
        创建默认配置文件
        
        Args:
            file_path: 配置文件路径
        """
        default_config = {
            'language': 'zh',
            'use_timezone': 'Asia/Shanghai',
            'llm_style': 'openai',
            'llm_api_key': 'your-api-key-here',
            'llm_base_url': 'https://api.openai.com/v1',
            'best_llm_model': 'gpt-4o-mini',
            'enable_event_embedding': True,
            'embedding_provider': 'openai',
            'embedding_model': 'text-embedding-3-small',
            'embedding_dim': 1536,
            'lindorm_table_host': 'localhost',
            'lindorm_table_port': 33060,
            'lindorm_table_username': 'root',
            'lindorm_table_database': 'memobase',
            'lindorm_search_host': 'localhost',
            'lindorm_search_port': 30070,
            'lindorm_search_use_ssl': False,
            'lindorm_search_username': 'root',
            'max_chat_blob_buffer_token_size': 8192,
            'max_chat_blob_buffer_process_token_size': 16384,
            'profile_strict_mode': False,
            'profile_validate_mode': True,
            'test_skip_persist': False
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Default config file created at {file_path}")


# 全局配置管理器实例
config_manager = ConfigManager()


def get_kafka_config() -> Dict:
    """获取Kafka配置的快捷函数"""
    return config_manager.get_kafka_config()


def get_database_config() -> Dict:
    """获取数据库配置的快捷函数"""
    return config_manager.get_database_config()


def get_memobase_config() -> Config:
    """获取LindormMemobase配置的快捷函数"""
    return config_manager.load_memobase_config()


def get_system_config() -> Dict:
    """获取系统配置的快捷函数"""
    return config_manager.get_system_config()