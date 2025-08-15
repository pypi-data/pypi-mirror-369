"""
装饰器模块

提供便捷的装饰器来快速包装Agent和定义技能。
"""

import logging
import functools
from typing import Any, Callable, List, Optional, Dict, Union

from ..config.agent_config import AgentConfig, AgentSkillConfig, AgentCapabilityConfig
from .wrapper import A2AWrapper

logger = logging.getLogger(__name__)


def a2a_agent(
    name: str,
    description: str = "",
    port: int = 10010,
    host: str = "0.0.0.0",
    skills: Optional[List[AgentSkillConfig]] = None,
    capabilities: Optional[AgentCapabilityConfig] = None,
    auto_run: bool = True,
    **config_kwargs
):
    """
    A2A Agent装饰器
    
    将一个类装饰为A2A Agent，自动处理包装和启动。
    
    Args:
        name: Agent名称
        description: Agent描述
        port: 服务端口
        host: 服务主机
        skills: 技能列表
        capabilities: 能力配置
        auto_run: 是否自动启动服务
        **config_kwargs: 额外配置参数
    
    Example:
        @a2a_agent(name="My Agent", port=10010)
        class MyAgent:
            def process(self, message: str) -> str:
                return f"处理: {message}"
    """
    def decorator(cls):
        # 创建配置
        config = AgentConfig(
            name=name,
            description=description,
            port=port,
            host=host,
            skills=skills or [],
            capabilities=capabilities,
            **config_kwargs
        )
        
        # 保存原始类
        original_cls = cls
        
        # 创建包装类
        class A2AAgentWrapper:
            def __init__(self, *args, **kwargs):
                # 创建原始Agent实例
                self.agent = original_cls(*args, **kwargs)
                
                # 创建A2A包装器
                self.wrapper = A2AWrapper(self.agent, config)
                
                logger.info(f"🎁 A2A Agent装饰器包装完成: {name}")
            
            def run(self, **uvicorn_kwargs):
                """启动A2A服务"""
                self.wrapper.run(**uvicorn_kwargs)
            
            def get_wrapper(self) -> A2AWrapper:
                """获取A2A包装器"""
                return self.wrapper
            
            def get_agent(self):
                """获取原始Agent"""
                return self.agent
            
            def __getattr__(self, name):
                """代理到原始Agent"""
                return getattr(self.agent, name)
        
        # 如果设置了auto_run，则在类定义时自动启动
        if auto_run:
            def auto_start():
                instance = A2AAgentWrapper()
                instance.run()
            
            # 添加启动方法到类
            A2AAgentWrapper.auto_start = staticmethod(auto_start)
        
        # 保留原始类的元数据
        A2AAgentWrapper.__name__ = cls.__name__
        A2AAgentWrapper.__doc__ = cls.__doc__
        A2AAgentWrapper.__module__ = cls.__module__
        
        return A2AAgentWrapper
    
    return decorator


def a2a_skill(
    skill_id: str,
    name: str,
    description: str,
    tags: Optional[List[str]] = None,
    examples: Optional[List[str]] = None
):
    """
    A2A技能装饰器
    
    将一个方法标记为A2A技能。
    
    Args:
        skill_id: 技能ID
        name: 技能名称
        description: 技能描述
        tags: 技能标签
        examples: 使用示例
    
    Example:
        class MyAgent:
            @a2a_skill("chat", "Chat", "Natural conversation")
            def chat(self, message: str) -> str:
                return f"回复: {message}"
    """
    def decorator(func):
        # 创建技能配置
        skill_config = AgentSkillConfig(
            id=skill_id,
            name=name,
            description=description,
            tags=tags or [],
            examples=examples or []
        )
        
        # 将技能配置附加到函数
        func._a2a_skill = skill_config
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._a2a_skill = skill_config
        return wrapper
    
    return decorator


def a2a_tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None
):
    """
    A2A工具装饰器
    
    将一个函数标记为A2A工具。
    
    Args:
        name: 工具名称
        description: 工具描述
        parameters: 工具参数定义
    
    Example:
        @a2a_tool("weather", "Get weather info")
        def get_weather(city: str) -> str:
            return f"Weather in {city}: Sunny"
    """
    def decorator(func):
        # 创建工具配置
        tool_config = {
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "function": func
        }
        
        # 将工具配置附加到函数
        func._a2a_tool = tool_config
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._a2a_tool = tool_config
        return wrapper
    
    return decorator


def async_handler(func):
    """
    异步处理装饰器
    
    确保函数能够正确处理异步调用。
    
    Example:
        @async_handler
        def process_message(self, message: str) -> str:
            # 这个方法会被自动包装为异步方法
            return "response"
    """
    if not asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return async_wrapper
    else:
        return func


def langchain_agent(
    name: str,
    description: str = "",
    tools: Optional[List[Any]] = None,
    memory: Optional[Any] = None,
    **config_kwargs
):
    """
    LangChain Agent专用装饰器
    
    专门为LangChain Agent设计的装饰器，提供更好的集成。
    
    Args:
        name: Agent名称
        description: Agent描述
        tools: LangChain工具列表
        memory: LangChain内存
        **config_kwargs: 额外配置
    
    Example:
        @langchain_agent(name="LangChain Bot", tools=[weather_tool])
        class MyLangChainAgent:
            def __init__(self):
                self.llm = ChatOpenAI()
                self.agent = create_react_agent(self.llm, tools)
    """
    def decorator(cls):
        # 设置LangChain特定配置
        langchain_config = {
            "tools": tools,
            "memory": memory,
            "verbose": config_kwargs.pop("verbose", False),
            "debug": config_kwargs.pop("debug", False)
        }
        
        # 使用a2a_agent装饰器，但添加LangChain配置
        return a2a_agent(
            name=name,
            description=description,
            langchain_config=langchain_config,
            **config_kwargs
        )(cls)
    
    return decorator


# 工具函数：从类中提取技能
def extract_skills_from_class(cls) -> List[AgentSkillConfig]:
    """
    从类中提取所有标记为技能的方法
    
    Args:
        cls: 要检查的类
        
    Returns:
        技能配置列表
    """
    skills = []
    
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if hasattr(attr, '_a2a_skill'):
            skills.append(attr._a2a_skill)
    
    return skills


def extract_tools_from_class(cls) -> List[Dict[str, Any]]:
    """
    从类中提取所有标记为工具的方法
    
    Args:
        cls: 要检查的类
        
    Returns:
        工具配置列表
    """
    tools = []
    
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if hasattr(attr, '_a2a_tool'):
            tools.append(attr._a2a_tool)
    
    return tools


# 配置装饰器
def with_config(config: Union[AgentConfig, Dict[str, Any]]):
    """
    配置装饰器
    
    使用预定义的配置来装饰Agent类。
    
    Args:
        config: Agent配置或配置字典
    
    Example:
        config = AgentConfig(name="My Agent", port=10010)
        
        @with_config(config)
        class MyAgent:
            def process(self, message: str) -> str:
                return "response"
    """
    def decorator(cls):
        if isinstance(config, dict):
            agent_config = AgentConfig(**config)
        else:
            agent_config = config
        
        # 提取类中的技能
        skills = extract_skills_from_class(cls)
        if skills:
            agent_config.skills.extend(skills)
        
        # 创建包装器
        class ConfiguredAgent:
            def __init__(self, *args, **kwargs):
                self.agent = cls(*args, **kwargs)
                self.wrapper = A2AWrapper(self.agent, agent_config)
            
            def run(self, **uvicorn_kwargs):
                self.wrapper.run(**uvicorn_kwargs)
            
            def get_wrapper(self) -> A2AWrapper:
                return self.wrapper
            
            def __getattr__(self, name):
                return getattr(self.agent, name)
        
        ConfiguredAgent.__name__ = cls.__name__
        ConfiguredAgent.__doc__ = cls.__doc__
        ConfiguredAgent.__module__ = cls.__module__
        
        return ConfiguredAgent
    
    return decorator


# 导入asyncio（如果需要）
try:
    import asyncio
except ImportError:
    asyncio = None
