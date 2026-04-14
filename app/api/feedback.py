"""
反馈 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Feedback, User
from app.schemas.schemas import FeedbackCreate, FeedbackReply, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["反馈"])


@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """提交反馈"""
    feedback = Feedback(
        user_id=user_id,
        content=feedback_data.content,
        screenshots=json.dumps(feedback_data.screenshots) if feedback_data.screenshots else None
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/my", response_model=List[FeedbackResponse])
async def my_feedbacks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取我的反馈列表"""
    feedbacks = db.query(Feedback).filter(
        Feedback.user_id == user_id
    ).order_by(Feedback.created_at.desc()).all()
    
    for f in feedbacks:
        if f.screenshots:
            f.screenshots = json.loads(f.screenshots)
    return feedbacks


# ============ 管理员接口 ============

feedback_router = APIRouter(prefix="/admin/feedback", tags=["管理员-反馈"])


@feedback_router.get("", response_model=List[FeedbackResponse])
async def list_feedbacks(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取所有反馈列表（管理员）"""
    query = db.query(Feedback)
    
    if status:
        query = query.filter(Feedback.status == status)
    
    total = query.count()
    feedbacks = query.order_by(Feedback.created_at.desc()).offset((page-1)*size).limit(size).all()
    
    for f in feedbacks:
        if f.screenshots:
            f.screenshots = json.loads(f.screenshots)
    
    return feedbacks


@feedback_router.put("/{feedback_id}/reply", response_model=FeedbackResponse)
async def reply_feedback(
    feedback_id: int,
    reply_data: FeedbackReply,
    admin_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """回复反馈（管理员）"""
    # 验证管理员权限
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin or admin.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    feedback.admin_reply = reply_data.reply_content
    feedback.status = "replied"
    from datetime import datetime
    feedback.replied_at = datetime.utcnow()
    
    db.commit()
    db.refresh(feedback)
    
    if feedback.screenshots:
        feedback.screenshots = json.loads(feedback.screenshots)
    return feedback
