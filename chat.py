"""
对话 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx
import json

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.config import settings
from app.models.models import ChatSession, ChatMessage
from app.schemas.schemas import (
    ChatMessageCreate, ChatMessageResponse,
    SessionCreate, SessionResponse, SessionListResponse
)

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建新会话"""
    session = ChatSession(
        user_id=user_id,
        title=session_data.title or "新对话"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[SessionListResponse])
async def list_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取会话列表"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.updated_at.desc()).all()
    return sessions


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除会话"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(session)
    db.commit()
    return {"message": "删除成功"}


@router.post("/session/{session_id}/message", response_model=ChatMessageResponse)
async def send_message(
    session_id: int,
    message: ChatMessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """发送消息并获取 AI 回复"""
    # 验证会话归属
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 保存用户消息
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=message.content
    )
    db.add(user_msg)
    
    # 获取历史消息（用于上下文）
    history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # 构建 messages 列表
    messages = []
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    messages.append({
        "role": "user", 
        "content": message.content
    })
    
    # 调用 MiniMax API
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.minimaxi.com/v1/text/chatcompletion_v2",
                headers={
                    "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "MiniMax-Text-01",
                    "messages": messages
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取 AI 回复
            choices = result.get("choices", [])
            if choices and len(choices) > 0:
                ai_content = choices[0].get("message", {}).get("content", "")
            else:
                ai_content = "抱歉，暂时无法获取回复"
            
            usage = result.get("usage", {})
            
    except Exception as e:
        ai_content = f"API 调用出错: {str(e)}"
        usage = {}
    
    # 保存 AI 回复
    ai_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_content,
        model_used="MiniMax-Text-01",
        tokens_used=usage.get("total_tokens")
    )
    db.add(ai_msg)
    
    # 更新会话时间
    session.updated_at = ai_msg.created_at
    
    db.commit()
    db.refresh(ai_msg)
    return ai_msg


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取会话详情"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session
