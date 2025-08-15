"""
消息处理工具

提供A2A消息的处理和转换功能。
"""

import uuid
from typing import Any, List, Optional, Dict

from a2a.types import Message, TextPart, Part


class MessageUtils:
    """消息处理工具类"""
    
    @staticmethod
    def extract_text_from_message(message: Message) -> str:
        """
        从A2A消息中提取文本内容
        
        Args:
            message: A2A消息对象
            
        Returns:
            提取的文本内容
        """
        if not message or not message.parts:
            return ""
        
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                text_parts.append(part.root.text)
            elif hasattr(part, 'text'):
                text_parts.append(part.text)
        
        return " ".join(text_parts)
    
    @staticmethod
    def create_text_message(
        text: str,
        role: str = "agent",
        task_id: Optional[str] = None,
        context_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Message:
        """
        创建文本消息
        
        Args:
            text: 消息文本
            role: 消息角色
            task_id: 任务ID
            context_id: 上下文ID
            message_id: 消息ID
            
        Returns:
            A2A消息对象
        """
        if message_id is None:
            message_id = str(uuid.uuid4())
        
        text_part = TextPart(text=text)
        part = Part(root=text_part)
        
        return Message(
            message_id=message_id,
            role=role,
            parts=[part],
            task_id=task_id,
            context_id=context_id
        )
    
    @staticmethod
    def create_multipart_message(
        parts: List[Dict[str, Any]],
        role: str = "agent",
        task_id: Optional[str] = None,
        context_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Message:
        """
        创建多部分消息
        
        Args:
            parts: 消息部分列表
            role: 消息角色
            task_id: 任务ID
            context_id: 上下文ID
            message_id: 消息ID
            
        Returns:
            A2A消息对象
        """
        if message_id is None:
            message_id = str(uuid.uuid4())
        
        message_parts = []
        for part_data in parts:
            if part_data.get("type") == "text":
                text_part = TextPart(text=part_data["content"])
                message_parts.append(Part(root=text_part))
            # 可以扩展支持其他类型的部分
        
        return Message(
            message_id=message_id,
            role=role,
            parts=message_parts,
            task_id=task_id,
            context_id=context_id
        )
    
    @staticmethod
    def message_to_dict(message: Message) -> Dict[str, Any]:
        """
        将消息转换为字典
        
        Args:
            message: A2A消息对象
            
        Returns:
            消息字典
        """
        return {
            "message_id": message.message_id,
            "role": message.role,
            "parts": [
                {
                    "type": "text",
                    "content": part.root.text if hasattr(part, 'root') and hasattr(part.root, 'text') else str(part)
                }
                for part in message.parts
            ],
            "task_id": message.task_id,
            "context_id": message.context_id
        }
    
    @staticmethod
    def dict_to_message(data: Dict[str, Any]) -> Message:
        """
        从字典创建消息
        
        Args:
            data: 消息字典
            
        Returns:
            A2A消息对象
        """
        parts = []
        for part_data in data.get("parts", []):
            if part_data.get("type") == "text":
                text_part = TextPart(text=part_data["content"])
                parts.append(Part(root=text_part))
        
        return Message(
            message_id=data.get("message_id", str(uuid.uuid4())),
            role=data.get("role", "user"),
            parts=parts,
            task_id=data.get("task_id"),
            context_id=data.get("context_id")
        )


# 便捷函数
def extract_text_from_message(message: Message) -> str:
    """提取消息文本的便捷函数"""
    return MessageUtils.extract_text_from_message(message)


def create_text_message(
    text: str,
    role: str = "agent",
    task_id: Optional[str] = None,
    context_id: Optional[str] = None
) -> Message:
    """创建文本消息的便捷函数"""
    return MessageUtils.create_text_message(text, role, task_id, context_id)


# 消息格式转换器
class MessageConverter:
    """消息格式转换器"""
    
    @staticmethod
    def to_langchain_format(message: Message) -> Dict[str, Any]:
        """
        转换为LangChain格式
        
        Args:
            message: A2A消息
            
        Returns:
            LangChain格式的消息
        """
        text = MessageUtils.extract_text_from_message(message)
        
        # LangChain常见格式
        return {
            "role": "human" if message.role == "user" else "ai",
            "content": text
        }
    
    @staticmethod
    def from_langchain_format(data: Dict[str, Any], task_id: Optional[str] = None) -> Message:
        """
        从LangChain格式创建消息
        
        Args:
            data: LangChain格式的消息
            task_id: 任务ID
            
        Returns:
            A2A消息
        """
        role = "user" if data.get("role") == "human" else "agent"
        content = data.get("content", "")
        
        return MessageUtils.create_text_message(content, role, task_id)
    
    @staticmethod
    def to_openai_format(message: Message) -> Dict[str, Any]:
        """
        转换为OpenAI格式
        
        Args:
            message: A2A消息
            
        Returns:
            OpenAI格式的消息
        """
        text = MessageUtils.extract_text_from_message(message)
        
        return {
            "role": "user" if message.role == "user" else "assistant",
            "content": text
        }
    
    @staticmethod
    def from_openai_format(data: Dict[str, Any], task_id: Optional[str] = None) -> Message:
        """
        从OpenAI格式创建消息
        
        Args:
            data: OpenAI格式的消息
            task_id: 任务ID
            
        Returns:
            A2A消息
        """
        role = "user" if data.get("role") == "user" else "agent"
        content = data.get("content", "")
        
        return MessageUtils.create_text_message(content, role, task_id)


# 消息历史管理
class MessageHistory:
    """消息历史管理器"""
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)
        
        # 保持消息数量限制
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """获取消息列表"""
        if limit is None:
            return self.messages.copy()
        else:
            return self.messages[-limit:]
    
    def get_conversation_text(self, limit: Optional[int] = None) -> str:
        """获取对话文本"""
        messages = self.get_messages(limit)
        
        conversation = []
        for msg in messages:
            text = MessageUtils.extract_text_from_message(msg)
            role = "用户" if msg.role == "user" else "助手"
            conversation.append(f"{role}: {text}")
        
        return "\n".join(conversation)
    
    def clear(self):
        """清空历史"""
        self.messages.clear()
    
    def to_langchain_format(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """转换为LangChain格式"""
        messages = self.get_messages(limit)
        return [MessageConverter.to_langchain_format(msg) for msg in messages]
    
    def to_openai_format(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """转换为OpenAI格式"""
        messages = self.get_messages(limit)
        return [MessageConverter.to_openai_format(msg) for msg in messages]
