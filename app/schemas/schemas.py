"""
Pydantic Schemas - 请求/响应模型
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ 用户 ============
class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    password: str
    invite_code: Optional[str] = None  # 邀请码


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ============ 邀请码 ============
class InviteCodeResponse(BaseModel):
    code: str
    code_type: str
    used_count: int
    max_uses: int
    status: str
    
    class Config:
        from_attributes = True


# ============ 对话 ============
class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 智囊任务 ============
class BrainTaskCreate(BaseModel):
    title: str
    task_type: str
    query: Optional[str] = None
    tags: Optional[List[str]] = []
    source: str = "manual"


class BrainTaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class BrainTaskResponse(BaseModel):
    id: int
    title: str
    task_type: str
    status: str
    tags: Optional[List[str]] = []
    source: str
    query: Optional[str] = None
    result_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 反馈 ============
class FeedbackCreate(BaseModel):
    content: str
    screenshots: Optional[List[str]] = []


class FeedbackReply(BaseModel):
    reply_content: str


class FeedbackResponse(BaseModel):
    id: int
    content: str
    screenshots: Optional[List[str]] = []
    status: str
    admin_reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 运营统计 ============
class AdminStats(BaseModel):
    total_users: int
    total_sessions: int
    total_tasks: int
    total_feedbacks: int
    pending_feedbacks: int
    today_active_users: int
    api_calls_today: int
