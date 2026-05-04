from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.student_task import model as st_model, schemas as st_schemas
from backend.user import model as user_model
from backend.task import model as task_model
from backend.user.router import get_current_user
from backend.integrations.twenty import create_zadacha_studenta_record


router = APIRouter(prefix="/student_task", tags=["student_task"])


@router.post("/", response_model=st_schemas.StudentTaskRead)
def create_student_task(payload: st_schemas.StudentTaskCreate, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    # ensure task exists
    task = db.query(task_model.Task).filter(task_model.Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # determine student_id: admin can assign to anyone. Regular users cannot create assignments.
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can assign tasks")

    student_id = payload.student_id or current_user.id

    default_deadline = datetime(2026, 11, 1)
    db_obj = st_model.StudentTask(
        student_id=student_id,
        task_id=payload.task_id,
        deadline=payload.deadline or default_deadline,
        status=payload.status or "assigned",
        completed_at=payload.completed_at,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    create_zadacha_studenta_record(db_obj)
    return db_obj


@router.get("/", response_model=List[st_schemas.StudentTaskRead])
def list_student_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    return db.query(st_model.StudentTask).filter(st_model.StudentTask.student_id == current_user.id).offset(skip).limit(limit).all()


@router.get("/my")
def my_tasks(db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    # return student_task entries with nested task info for current user
    rows = db.query(st_model.StudentTask).filter(st_model.StudentTask.student_id == current_user.id).all()
    result = []
    for r in rows:
        task = db.query(task_model.Task).filter(task_model.Task.id == r.task_id).first()
        result.append({
            "id": r.id,
            "deadline": r.deadline,
            "status": r.status,
            "completed_at": r.completed_at,
            "task": {"id": task.id, "title": task.title, "description": task.description} if task else None,
        })
    return result


@router.get("/{st_id}", response_model=st_schemas.StudentTaskRead)
def get_student_task(st_id: int, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    obj = db.query(st_model.StudentTask).filter(st_model.StudentTask.id == st_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    if obj.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return obj


@router.put("/{st_id}", response_model=st_schemas.StudentTaskRead)
def update_student_task(st_id: int, payload: st_schemas.StudentTaskUpdate, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    obj = db.query(st_model.StudentTask).filter(st_model.StudentTask.id == st_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    if obj.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{st_id}")
def delete_student_task(st_id: int, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    obj = db.query(st_model.StudentTask).filter(st_model.StudentTask.id == st_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    if obj.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    db.delete(obj)
    db.commit()
    return {"detail": "deleted"}


@router.post("/{st_id}/complete")
def complete_student_task(st_id: int, db: Session = Depends(get_db), current_user: user_model.Student = Depends(get_current_user)):
    obj = db.query(st_model.StudentTask).filter(st_model.StudentTask.id == st_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    if obj.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    from datetime import datetime
    obj.status = "completed"
    obj.completed_at = datetime.utcnow()
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"detail": "completed", "id": obj.id}