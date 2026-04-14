from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.task import model as task_model, schemas as task_schemas


router = APIRouter(prefix="/task", tags=["task"])


@router.post("/", response_model=task_schemas.TaskRead)
def create_task(payload: task_schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = task_model.Task(**payload.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[task_schemas.TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(task_model.Task).offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=task_schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=task_schemas.TaskRead)
def update_task(task_id: int, payload: task_schemas.TaskCreate, db: Session = Depends(get_db)):
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
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "deleted"}



@router.post("/seed", response_model=List[task_schemas.TaskRead])
def seed_tasks(db: Session = Depends(get_db)):
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