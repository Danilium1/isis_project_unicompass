from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.task import model as task_model, schemas as task_schemas
from backend.user.router import get_current_user
from backend.user import model as user_model
from backend.student_task import model as st_model


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/", response_model=task_schemas.TaskRead)
def create_task(payload: task_schemas.TaskCreate, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db_task = task_model.Task(**payload.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[task_schemas.TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    # Admins see all tasks; regular users see only tasks assigned to them
    if current_user.is_admin:
        return db.query(task_model.Task).offset(skip).limit(limit).all()
    # find tasks assigned to this student
    joins = db.query(task_model.Task).join(st_model.StudentTask, task_model.Task.id == st_model.StudentTask.task_id).filter(st_model.StudentTask.student_id == current_user.id).offset(skip).limit(limit).all()
    return joins


@router.get("/{task_id}", response_model=task_schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # if non-admin, ensure task is assigned to them
    if not current_user.is_admin:
        assigned = db.query(st_model.StudentTask).filter(st_model.StudentTask.task_id == task_id, st_model.StudentTask.student_id == current_user.id).first()
        if not assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return task


@router.put("/{task_id}", response_model=task_schemas.TaskRead)
def update_task(task_id: int, payload: task_schemas.TaskCreate, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "deleted"}



@router.post("/seed", response_model=List[task_schemas.TaskRead])
def seed_tasks(db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    samples = [
        {"title": "оформить паспорт", "description": "оформить паспорт что бы не исключили из страны"},
        {"title": "подать заявление", "description": "подать заявление на участие в проекте"},
        {"title": "подготовить отчёт", "description": "собрать все материалы и оформить отчёт"},
        {"title": "пройти тестирование", "description": "пройти входное тестирование для должности"},
        {"title": "сдать курсовую", "description": "закончить и сдать курсовую работу"},
        {"title": "обновить резюме", "description": "добавить новые достижения и опыт"},
        {"title": "записаться на курс", "description": "найти и записаться на профильный курс"},
        {"title": "написать сопроводительное", "description": "подготовить сопроводительное письмо"},
        {"title": "сделать презентацию", "description": "подготовить презентацию для защищи"},
        {"title": "проверить почту", "description": "ответить на важные письма и уведомления"},
    ]

    created = []
    for s in samples:
        exists = db.query(task_model.Task).filter(task_model.Task.title == s["title"]).first()
        if exists:
            created.append(exists)
            continue
        t = task_model.Task(**s)
        db.add(t)
        db.commit()
        db.refresh(t)
        created.append(t)

    return created