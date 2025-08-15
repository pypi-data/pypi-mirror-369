"""
Agent执行器

提供不同类型Agent的执行器实现，支持：
- 基础Agent执行器
- LangChain Agent执行器
- 自动适配不同的Agent接口
"""

import logging
import uuid
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, TextPart, Part

logger = logging.getLogger(__name__)


class BaseAgentExecutor(AgentExecutor, ABC):
    """
    基础Agent执行器
    
    提供A2A协议的标准实现，具体的Agent只需要实现process_message方法。
    """
    
    def __init__(self, agent: Any, name: str, description: str):
        """
        初始化执行器
        
        Args:
            agent: 原始Agent实例
            name: Agent名称
            description: Agent描述
        """
        super().__init__()
        self.agent = agent
        self.name = name
        self.description = description
        self._message_handler = self._detect_message_handler()
        
        logger.info(f"🤖 初始化Agent执行器: {self.name}")
    
    def _detect_message_handler(self) -> Callable:
        """自动检测Agent的消息处理方法"""
        # 常见的方法名
        method_names = [
            'process', 'chat', 'handle', 'invoke', 'run', 
            'process_message', 'handle_message', 'respond'
        ]
        
        for method_name in method_names:
            if hasattr(self.agent, method_name):
                method = getattr(self.agent, method_name)
                if callable(method):
                    logger.info(f"🔍 检测到消息处理方法: {method_name}")
                    return method
        
        raise ValueError(f"无法找到Agent的消息处理方法，请确保Agent有以下方法之一: {method_names}")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        执行Agent任务
        
        Args:
            context: 请求上下文
            event_queue: 事件队列
        """
        try:
            logger.info(f"🚀 开始执行任务: {context.task_id}")
            
            # 提取用户消息
            user_message = self._extract_user_message(context)
            logger.info(f"📝 用户消息: {user_message}")
            
            # 调用Agent处理消息
            response = await self._call_agent_handler(user_message, context)
            
            # 处理响应
            response_text = self._process_response(response)
            
            # 创建响应消息
            response_message = self._create_response_message(response_text, context.task_id)
            response_message.context_id = context.message.context_id if context.message else str(uuid.uuid4())
            
            # 发布响应事件
            await event_queue.enqueue_event(response_message)
            
            logger.info(f"✅ 任务完成: {context.task_id}")
            
        except Exception as e:
            logger.error(f"❌ 任务执行失败: {e}")
            await self._handle_error(e, context, event_queue)
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """取消任务"""
        logger.info(f"🚫 取消任务: {context.task_id}")
        
        cancel_message = self._create_response_message("任务已被取消", context.task_id)
        cancel_message.context_id = context.message.context_id if context.message else str(uuid.uuid4())
        await event_queue.enqueue_event(cancel_message)
    
    async def _call_agent_handler(self, message: str, context: RequestContext) -> Any:
        """调用Agent的处理方法"""
        handler = self._message_handler
        
        # 检查方法签名
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
        
        # 根据参数数量调用不同的方式
        if len(params) == 1:
            # 只接受消息
            if inspect.iscoroutinefunction(handler):
                return await handler(message)
            else:
                return handler(message)
        elif len(params) >= 2:
            # 接受消息和上下文
            context_dict = {
                "task_id": context.task_id,
                "message_id": context.message.message_id if context.message else None,
                "context_id": context.message.context_id if context.message else None
            }
            
            if inspect.iscoroutinefunction(handler):
                return await handler(message, context_dict)
            else:
                return handler(message, context_dict)
        else:
            raise ValueError(f"Agent处理方法 {handler.__name__} 参数不正确")
    
    def _process_response(self, response: Any) -> str:
        """处理Agent响应"""
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            # 尝试提取常见的响应字段
            for key in ['response', 'output', 'result', 'answer', 'content']:
                if key in response:
                    return str(response[key])
            # 如果没有找到，返回整个字典的字符串表示
            return str(response)
        else:
            return str(response)
    
    def _extract_user_message(self, context: RequestContext) -> str:
        """从请求上下文中提取用户消息"""
        user_message = ""
        if context.message and context.message.parts:
            for part in context.message.parts:
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    user_message += part.root.text
                elif hasattr(part, 'text'):
                    user_message += part.text
        return user_message
    
    def _create_response_message(self, text: str, task_id: str) -> Message:
        """创建响应消息"""
        response_part = TextPart(text=text)
        return Message(
            message_id=str(uuid.uuid4()),
            role="agent",
            parts=[Part(root=response_part)],
            task_id=task_id
        )
    
    async def _handle_error(self, error: Exception, context: RequestContext, event_queue: EventQueue) -> None:
        """处理错误"""
        error_message = f"抱歉，处理您的请求时出现错误：{str(error)}"
        
        error_response = self._create_response_message(error_message, context.task_id)
        error_response.context_id = context.message.context_id if context.message else str(uuid.uuid4())
        
        await event_queue.enqueue_event(error_response)


class LangChainAgentExecutor(BaseAgentExecutor):
    """
    LangChain Agent执行器
    
    专门为LangChain Agent优化的执行器，支持：
    - 自动检测LangChain Agent类型
    - 工具调用支持
    - 内存管理
    - 流式响应（可选）
    """
    
    def __init__(self, agent: Any, name: str, description: str, **kwargs):
        """
        初始化LangChain执行器
        
        Args:
            agent: LangChain Agent实例
            name: Agent名称
            description: Agent描述
            **kwargs: 额外配置
        """
        super().__init__(agent, name, description)
        self.langchain_config = kwargs
        self._detect_langchain_type()
        
        logger.info(f"🦜 初始化LangChain Agent执行器: {self.name}")
    
    def _detect_langchain_type(self):
        """检测LangChain Agent类型"""
        agent_type = type(self.agent).__name__
        logger.info(f"🔍 检测到LangChain Agent类型: {agent_type}")
        
        # 检测是否有特定的LangChain方法
        langchain_methods = ['invoke', 'stream', 'batch', 'ainvoke', 'astream']
        available_methods = [method for method in langchain_methods if hasattr(self.agent, method)]
        
        if available_methods:
            logger.info(f"🛠️ 可用的LangChain方法: {available_methods}")
            # 优先使用异步方法
            if 'ainvoke' in available_methods:
                self._message_handler = self.agent.ainvoke
            elif 'invoke' in available_methods:
                self._message_handler = self.agent.invoke
    
    async def _call_agent_handler(self, message: str, context: RequestContext) -> Any:
        """调用LangChain Agent"""
        handler = self._message_handler
        
        # LangChain通常接受字典格式的输入
        if hasattr(self.agent, 'invoke') or hasattr(self.agent, 'ainvoke'):
            # 构建LangChain输入格式
            langchain_input = self._build_langchain_input(message, context)
            
            if inspect.iscoroutinefunction(handler):
                return await handler(langchain_input)
            else:
                return handler(langchain_input)
        else:
            # 回退到基础方法
            return await super()._call_agent_handler(message, context)
    
    def _build_langchain_input(self, message: str, context: RequestContext) -> Dict[str, Any]:
        """构建LangChain输入格式"""
        # 常见的LangChain输入格式
        input_formats = [
            {"input": message},
            {"messages": [{"role": "user", "content": message}]},
            {"query": message},
            {"question": message}
        ]
        
        # 尝试检测Agent期望的输入格式
        if hasattr(self.agent, 'input_keys'):
            keys = self.agent.input_keys
            if 'input' in keys:
                return {"input": message}
            elif 'query' in keys:
                return {"query": message}
            elif 'question' in keys:
                return {"question": message}
        
        # 默认使用input格式
        return {"input": message}
    
    def _process_response(self, response: Any) -> str:
        """处理LangChain响应"""
        # LangChain常见的响应格式
        if isinstance(response, dict):
            # 尝试提取LangChain常见的输出字段
            for key in ['output', 'result', 'answer', 'response', 'content']:
                if key in response:
                    return str(response[key])
        
        # 检查是否是LangChain消息对象
        if hasattr(response, 'content'):
            return response.content
        
        # 回退到基础处理
        return super()._process_response(response)


# Agent执行器工厂
class ExecutorFactory:
    """执行器工厂，自动选择合适的执行器"""
    
    @staticmethod
    def create_executor(agent: Any, name: str, description: str, **kwargs) -> BaseAgentExecutor:
        """
        自动创建合适的执行器
        
        Args:
            agent: Agent实例
            name: Agent名称
            description: Agent描述
            **kwargs: 额外配置
            
        Returns:
            合适的执行器实例
        """
        # 检测是否是LangChain Agent
        if ExecutorFactory._is_langchain_agent(agent):
            logger.info("🦜 检测到LangChain Agent，使用LangChain执行器")
            return LangChainAgentExecutor(agent, name, description, **kwargs)
        else:
            logger.info("🤖 使用基础Agent执行器")
            return BaseAgentExecutor(agent, name, description)
    
    @staticmethod
    def _is_langchain_agent(agent: Any) -> bool:
        """检测是否是LangChain Agent"""
        # 检查模块名
        module_name = type(agent).__module__
        if 'langchain' in module_name.lower():
            return True
        
        # 检查是否有LangChain特有的方法
        langchain_methods = ['invoke', 'stream', 'batch', 'ainvoke', 'astream']
        if any(hasattr(agent, method) for method in langchain_methods):
            return True
        
        # 检查是否有LangChain特有的属性
        langchain_attrs = ['input_keys', 'output_keys', 'memory', 'tools']
        if any(hasattr(agent, attr) for attr in langchain_attrs):
            return True
        
        return False
