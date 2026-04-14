"""
认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    get_password_hash, verify_password, 
    create_access_token, create_refresh_token, decode_token
)
from app.core.config import settings
from app.models.models import User, InviteCode, InviteRecord
from app.schemas.schemas import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 检查邀请码（如果有）
    invite_code = None
    if user_data.invite_code:
        invite_code = db.query(InviteCode).filter(
            InviteCode.code == user_data.invite_code,
            InviteCode.status == 'active'
        ).first()
        if not invite_code:
            raise HTTPException(status_code=400, detail="无效的邀请码")
        if invite_code.used_count >= invite_code.max_uses:
            raise HTTPException(status_code=400, detail="邀请码已用完")
    
    # 创建用户
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.email.split("@")[0]
    )
    db.add(user)
    db.flush()
    
    # 更新邀请码使用次数
    if invite_code:
        invite_code.used_count += 1
        record = InviteRecord(
            code_id=invite_code.id,
            invited_user_id=user.id
        )
        db.add(record)
        
        # 如果是B码且用完了，给A码持有者增加名额
        if invite_code.code_type == 'B' and invite_code.used_count >= invite_code.max_uses:
            if invite_code.parent_code:
                parent_code = db.query(InviteCode).filter(
                    InviteCode.code == invite_code.parent_code
                ).first()
                if parent_code:
                    parent_code.max_uses += 1
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    if user.status == 'banned':
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    # 创建 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """刷新 Token"""
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的刷新令牌")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.status == 'banned':
        raise HTTPException(status_code=401, detail="用户不存在或已被禁用")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(__import__('app.core.security', fromlist=['get_current_user_id']).get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
