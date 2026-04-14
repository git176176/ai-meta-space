"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(Enum('user', 'admin', 'super_admin'), default='user')
    status = Column(Enum('active', 'banned'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("BrainTask", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    invite_codes = relationship("InviteCode", back_populates="owner", foreign_keys="InviteCode.owner_id")


class ChatSession(Base):
    """对话会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(Enum('user', 'assistant', 'system'), nullable=False)
    content = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=True)  # 使用的AI模型
    tokens_used = Column(Integer, nullable=True)  # 消耗的token数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")


class BrainTask(Base):
    """智囊任务表"""
    __tablename__ = "brain_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    task_type = Column(Enum(
        'search',           # 全网搜索
        'news_summary',     # 新闻总结
        'hotspot_tracking', # 热点跟踪
        'outline',          # 自动提纲
        'report',           # 生成报告
        'schedule'          # 日程规划
    ), nullable=False)
    status = Column(Enum('todo', 'doing', 'done'), default='todo')
    tags = Column(Text, nullable=True)  # JSON格式存储标签
    source = Column(Enum('brain', 'chat', 'manual'), default='manual')  # 来源
    query = Column(Text, nullable=True)  # 搜索关键词等
    result_summary = Column(Text, nullable=True)  # 结果总结
    result_data = Column(Text, nullable=True)  # 详细结果JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="tasks")


class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedbacks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    screenshots = Column(Text, nullable=True)  # JSON格式存储截图URL列表
    status = Column(Enum('pending', 'replied', 'closed'), default='pending')
    admin_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="feedbacks")


class InviteCode(Base):
    """邀请码表"""
    __tablename__ = "invite_codes"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    code_type = Column(Enum('A', 'B'), nullable=False)  # A=主码, B=子码
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    parent_code = Column(String(20), nullable=True)  # B码所属的A码
    used_count = Column(Integer, default=0)
    max_uses = Column(Integer, default=3)
    status = Column(Enum('active', 'expired', 'revoked'), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    owner = relationship("User", back_populates="invite_codes", foreign_keys=[owner_id])
    records = relationship("InviteRecord", back_populates="invite_code")


class InviteRecord(Base):
    """邀请记录表"""
    __tablename__ = "invite_records"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code_id = Column(BigInteger, ForeignKey("invite_codes.id"), nullable=False)
    invited_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    invite_code = relationship("InviteCode", back_populates="records")
    invited_user = relationship("User", foreign_keys=[invited_user_id])
