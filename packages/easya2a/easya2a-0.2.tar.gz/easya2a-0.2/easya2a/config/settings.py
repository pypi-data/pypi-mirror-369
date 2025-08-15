"""
环境设置和配置管理

处理环境变量、默认配置和全局设置。
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """全局设置"""
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 默认服务器配置
    default_host: str = "0.0.0.0"
    default_port: int = 10010
    
    # A2A协议配置
    protocol_version: str = "0.3.0"
    transport: str = "JSONRPC"
    
    # LangChain配置
    langchain_verbose: bool = False
    langchain_debug: bool = False
    
    # 环境变量前缀
    env_prefix: str = "EASYA2A_"
    
    def __post_init__(self):
        """从环境变量加载配置"""
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载设置"""
        # 日志配置
        self.log_level = os.getenv(f"{self.env_prefix}LOG_LEVEL", self.log_level)
        
        # 服务器配置
        self.default_host = os.getenv(f"{self.env_prefix}HOST", self.default_host)
        self.default_port = int(os.getenv(f"{self.env_prefix}PORT", str(self.default_port)))
        
        # LangChain配置
        self.langchain_verbose = os.getenv(f"{self.env_prefix}LANGCHAIN_VERBOSE", "false").lower() == "true"
        self.langchain_debug = os.getenv(f"{self.env_prefix}LANGCHAIN_DEBUG", "false").lower() == "true"
    
    def get_langchain_config(self) -> Dict[str, Any]:
        """获取LangChain配置"""
        return {
            "verbose": self.langchain_verbose,
            "debug": self.langchain_debug
        }


# 全局设置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局设置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def setup_logging(settings: Optional[Settings] = None):
    """设置日志配置"""
    import logging
    
    if settings is None:
        settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )


# 环境变量工具函数
def load_env_file(env_file: Optional[Path] = None):
    """加载环境变量文件"""
    try:
        from dotenv import load_dotenv
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
    except ImportError:
        pass  # dotenv不是必需的


def get_env_config() -> Dict[str, str]:
    """获取所有A2A相关的环境变量"""
    prefix = get_settings().env_prefix
    return {
        key[len(prefix):].lower(): value
        for key, value in os.environ.items()
        if key.startswith(prefix)
    }


# 配置验证
def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置的有效性"""
    required_fields = ["name"]
    
    for field in required_fields:
        if field not in config or not config[field]:
            raise ValueError(f"Required field '{field}' is missing or empty")
    
    # 验证端口范围
    if "port" in config:
        port = config["port"]
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")
    
    return True


# 配置模板
class ConfigTemplates:
    """预定义的配置模板"""
    
    @staticmethod
    def development() -> Dict[str, Any]:
        """开发环境配置"""
        return {
            "host": "localhost",
            "port": 10010,
            "log_level": "DEBUG",
            "langchain_verbose": True,
            "langchain_debug": True
        }
    
    @staticmethod
    def production() -> Dict[str, Any]:
        """生产环境配置"""
        return {
            "host": "0.0.0.0",
            "port": 10010,
            "log_level": "INFO",
            "langchain_verbose": False,
            "langchain_debug": False
        }
    
    @staticmethod
    def testing() -> Dict[str, Any]:
        """测试环境配置"""
        return {
            "host": "localhost",
            "port": 0,  # 随机端口
            "log_level": "WARNING",
            "langchain_verbose": False,
            "langchain_debug": False
        }
