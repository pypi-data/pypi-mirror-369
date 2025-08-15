"""
Agent配置管理

定义Agent的配置结构，包括基本信息、技能、能力等。
支持灵活配置和智能默认值。
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentSkillConfig:
    """Agent技能配置"""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "examples": self.examples
        }


@dataclass
class AgentCapabilityConfig:
    """Agent能力配置"""
    streaming: bool = False
    push_notifications: bool = True
    state_transition_history: bool = False
    multimodal: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "streaming": self.streaming,
            "push_notifications": self.push_notifications,
            "state_transition_history": self.state_transition_history,
            "multimodal": self.multimodal
        }


@dataclass
class AgentConfig:
    """Agent完整配置"""
    
    # 基本信息
    name: str
    description: str = ""
    version: str = "1.0.0"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 10010

    # Agent Card URL (独立配置，用于A2A协议通信)
    agent_url: Optional[str] = None
    
    # 提供商信息
    provider_organization: str = "EasyA2A Agent Services"
    provider_url: Optional[str] = None
    
    # 技能和能力
    skills: List[AgentSkillConfig] = field(default_factory=list)
    capabilities: Optional[AgentCapabilityConfig] = None
    
    # 输入输出模式
    default_input_modes: List[str] = field(default_factory=lambda: ["text", "text/plain"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text", "text/plain"])
    
    # LangChain特定配置
    langchain_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置Agent URL (用于A2A协议通信)
        if self.agent_url is None:
            # 默认使用服务器地址，但可以独立配置
            self.agent_url = f"http://{self.host}:{self.port}/"

        # 自动生成provider_url
        if self.provider_url is None:
            self.provider_url = self.agent_url
        
        # 设置默认能力
        if self.capabilities is None:
            self.capabilities = AgentCapabilityConfig()
        
        # 如果没有技能，创建默认技能
        if not self.skills:
            self.skills = [
                AgentSkillConfig(
                    id="general_assistance",
                    name="General Assistance", 
                    description=self.description or "General purpose AI assistant",
                    tags=["assistance", "general", "langchain"],
                    examples=[
                        "你好",
                        "帮我处理一下这个问题",
                        "我需要帮助"
                    ]
                )
            ]
    
    def add_skill(self, skill: AgentSkillConfig) -> None:
        """添加技能"""
        self.skills.append(skill)
    
    def get_agent_card_data(self) -> Dict[str, Any]:
        """获取Agent Card数据"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "url": self.agent_url,  # 使用独立的agent_url
            "provider": {
                "organization": self.provider_organization,
                "url": self.provider_url
            },
            "capabilities": self.capabilities.to_dict(),
            "default_input_modes": self.default_input_modes,
            "default_output_modes": self.default_output_modes,
            "skills": [skill.to_dict() for skill in self.skills]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """从字典创建配置"""
        # 处理技能
        skills = []
        if "skills" in data:
            for skill_data in data["skills"]:
                skills.append(AgentSkillConfig(**skill_data))
        
        # 处理能力
        capabilities = None
        if "capabilities" in data:
            capabilities = AgentCapabilityConfig(**data["capabilities"])
        
        # 移除嵌套对象，避免重复处理
        config_data = data.copy()
        config_data.pop("skills", None)
        config_data.pop("capabilities", None)
        
        return cls(
            skills=skills,
            capabilities=capabilities,
            **config_data
        )
    
    @classmethod
    def from_file(cls, file_path: Path) -> "AgentConfig":
        """从文件加载配置"""
        import json
        import yaml
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")
        
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: Path) -> None:
        """保存配置到文件"""
        import json
        import yaml
        
        data = self.get_agent_card_data()
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")


# 快速配置构建器
class ConfigBuilder:
    """配置构建器，提供链式调用接口"""

    def __init__(self, name: str, description: str = ""):
        self.config = AgentConfig(name=name, description=description)

    def port(self, port: int) -> "ConfigBuilder":
        """设置端口"""
        self.config.port = port
        return self

    def host(self, host: str) -> "ConfigBuilder":
        """设置主机"""
        self.config.host = host
        return self

    def agent_url(self, url: str) -> "ConfigBuilder":
        """设置Agent URL（用于A2A协议通信）"""
        self.config.agent_url = url
        return self

    def add_chat_skill(self) -> "ConfigBuilder":
        """添加聊天技能"""
        self.config.add_skill(SkillTemplates.chat_skill())
        return self

    def add_qa_skill(self) -> "ConfigBuilder":
        """添加问答技能"""
        self.config.add_skill(SkillTemplates.qa_skill())
        return self

    def add_tool_skill(self) -> "ConfigBuilder":
        """添加工具调用技能"""
        self.config.add_skill(SkillTemplates.tool_calling_skill())
        return self

    def enable_streaming(self) -> "ConfigBuilder":
        """启用流式响应"""
        self.config.capabilities.streaming = True
        return self

    def enable_multimodal(self) -> "ConfigBuilder":
        """启用多模态"""
        self.config.capabilities.multimodal = True
        return self

    def build(self) -> AgentConfig:
        """构建配置"""
        return self.config


# 预定义的技能配置
class SkillTemplates:
    """常用技能模板"""
    
    @staticmethod
    def chat_skill() -> AgentSkillConfig:
        """聊天技能"""
        return AgentSkillConfig(
            id="chat",
            name="Chat",
            description="Natural language conversation",
            tags=["chat", "conversation", "nlp"],
            examples=[
                "你好，今天天气怎么样？",
                "跟我聊聊天吧",
                "Hello, how are you?"
            ]
        )
    
    @staticmethod
    def qa_skill() -> AgentSkillConfig:
        """问答技能"""
        return AgentSkillConfig(
            id="qa",
            name="Question Answering",
            description="Answer questions based on knowledge",
            tags=["qa", "knowledge", "information"],
            examples=[
                "什么是人工智能？",
                "解释一下机器学习",
                "Python是什么？"
            ]
        )
    
    @staticmethod
    def tool_calling_skill() -> AgentSkillConfig:
        """工具调用技能"""
        return AgentSkillConfig(
            id="tool_calling",
            name="Tool Calling",
            description="Call external tools and APIs",
            tags=["tools", "api", "integration"],
            examples=[
                "查询天气信息",
                "搜索相关资料",
                "计算数学问题"
            ]
        )


# 预定义的能力配置
class CapabilityTemplates:
    """常用能力模板"""
    
    @staticmethod
    def basic() -> AgentCapabilityConfig:
        """基础能力"""
        return AgentCapabilityConfig(
            streaming=False,
            push_notifications=True,
            state_transition_history=False,
            multimodal=False
        )
    
    @staticmethod
    def advanced() -> AgentCapabilityConfig:
        """高级能力"""
        return AgentCapabilityConfig(
            streaming=True,
            push_notifications=True,
            state_transition_history=True,
            multimodal=True
        )
    
    @staticmethod
    def streaming() -> AgentCapabilityConfig:
        """流式能力"""
        return AgentCapabilityConfig(
            streaming=True,
            push_notifications=True,
            state_transition_history=False,
            multimodal=False
        )
