"""
配置管理模块

提供A2A Agent的配置管理功能，包括：
- Agent基本信息配置
- 技能和能力配置  
- 服务器配置
- 环境变量管理
"""

from .agent_config import AgentConfig, AgentSkillConfig, AgentCapabilityConfig
from .settings import Settings, get_settings

__all__ = [
    "AgentConfig",
    "AgentSkillConfig", 
    "AgentCapabilityConfig",
    "Settings",
    "get_settings",
]
