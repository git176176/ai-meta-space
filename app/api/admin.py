"""
管理后台 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.models import User, ChatSession, BrainTask, Feedback
from app.schemas.schemas import AdminStats

router = APIRouter(prefix="/admin", tags=["管理员"])


async def verify_admin(user_id: int, db: Session) -> bool:
    """验证管理员权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role not in ['admin', 'super_admin']:
        return False
    return True


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取运营统计"""
    if not await verify_admin(user_id, db):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 总用户数
    total_users = db.query(User).count()
    
    # 今日活跃用户（今天有会话的）
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    today_active = db.query(ChatSession.user_id).filter(
        ChatSession.created_at >= today_start
    ).distinct().count()
    
    # 会话总数
    total_sessions = db.query(ChatSession).count()
    
    # 任务总数
    total_tasks = db.query(BrainTask).count()
    
    # 反馈统计
    total_feedbacks = db.query(Feedback).count()
    pending_feedbacks = db.query(Feedback).filter(Feedback.status == 'pending').count()
    
    return AdminStats(
        total_users=total_users,
        total_sessions=total_sessions,
        total_tasks=total_tasks,
        total_feedbacks=total_feedbacks,
        pending_feedbacks=pending_feedbacks,
        today_active_users=today_active,
        api_calls_today=0  # TODO: 实现API调用计数
    )


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: str = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """用户列表"""
    if not await verify_admin(user_id, db):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page-1)*size).limit(size).all()
    
    return {"total": total, "users": users}


@router.put("/user/{target_user_id}/role")
async def update_user_role(
    target_user_id: int,
    new_role: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """修改用户角色"""
    if not await verify_admin(user_id, db):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.role = new_role
    db.commit()
    return {"message": "修改成功"}


@router.put("/user/{target_user_id}/status")
async def update_user_status(
    target_user_id: int,
    new_status: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """修改用户状态"""
    if not await verify_admin(user_id, db):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.status = new_status
    db.commit()
    return {"message": "修改成功"}
