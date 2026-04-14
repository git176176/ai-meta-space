"""
智囊任务 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.models import BrainTask
from app.schemas.schemas import BrainTaskCreate, BrainTaskUpdate, BrainTaskResponse

router = APIRouter(prefix="/brain", tags=["智囊"])


@router.post("/tasks", response_model=BrainTaskResponse)
async def create_task(
    task_data: BrainTaskCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建智囊任务"""
    task = BrainTask(
        user_id=user_id,
        title=task_data.title,
        task_type=task_data.task_type,
        query=task_data.query,
        tags=json.dumps(task_data.tags) if task_data.tags else None,
        source=task_data.source
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=List[BrainTaskResponse])
async def list_tasks(
    status: str = None,
    task_type: str = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(BrainTask).filter(BrainTask.user_id == user_id)
    
    if status:
        query = query.filter(BrainTask.status == status)
    if task_type:
        query = query.filter(BrainTask.task_type == task_type)
    
    tasks = query.order_by(BrainTask.updated_at.desc()).all()
    
    # 转换 tags JSON 为列表
    for task in tasks:
        if task.tags:
            task.tags = json.loads(task.tags)
    
    return tasks


@router.get("/task/{task_id}", response_model=BrainTaskResponse)
async def get_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(BrainTask).filter(
        BrainTask.id == task_id,
        BrainTask.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.tags:
        task.tags = json.loads(task.tags)
    return task


@router.put("/task/{task_id}", response_model=BrainTaskResponse)
async def update_task(
    task_id: int,
    task_data: BrainTaskUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(BrainTask).filter(
        BrainTask.id == task_id,
        BrainTask.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.tags is not None:
        task.tags = json.dumps(task_data.tags)
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/task/{task_id}")
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除任务"""
    task = db.query(BrainTask).filter(
        BrainTask.id == task_id,
        BrainTask.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    return {"message": "删除成功"}


@router.post("/task/{task_id}/execute")
async def execute_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """执行任务（搜索/总结/生成报告等）"""
    task = db.query(BrainTask).filter(
        BrainTask.id == task_id,
        BrainTask.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # TODO: 根据 task_type 执行不同的 AI 任务
    # 目前返回模拟数据
    task.result_summary = f"已完成 {task.task_type} 任务的结果"
    task.result_data = json.dumps({
        "status": "completed",
        "message": "模拟执行完成"
    })
    task.status = "done"
    
    db.commit()
    db.refresh(task)
    
    if task.tags:
        task.tags = json.loads(task.tags)
    return task
