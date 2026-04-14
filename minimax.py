"""
MiniMax AI API 服务
"""
import httpx
from typing import List, Optional, Dict, Any
from app.core.config import settings


class MiniMaxService:
    """MiniMax AI 对话服务"""
    
    BASE_URL = "https://api.minimaxi.com/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "MiniMax-Text-01",
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用 MiniMax 文本补全 API
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            model: 模型名称，默认 MiniMax-Text-01
        
        Returns:
            API 响应
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            # MiniMax 文本补全 API
            response = await client.post(
                f"{self.BASE_URL}/text/chatcompletion_v2",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "MiniMax-Text-01",
        **kwargs
    ):
        """
        流式调用 MiniMax API
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.BASE_URL}/text/chatcompletion_v2",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    **kwargs
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield line[6:]  # 去掉 "data: " 前缀


# 全局单例
minimax_service = MiniMaxService()


async def call_minimax(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """简单的对话调用"""
    return await minimax_service.chat(messages=messages)
