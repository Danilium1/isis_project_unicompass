from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import engine, Base, init_db, get_db
from backend.user import model as user_model, schemas as user_schemas
from backend.task import model as task_model
from backend.student_task import model as st_model, schemas as st_schemas
from backend.user.router import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset-db")
def reset_db():
    """Drop all tables and recreate them. Development-only helper."""
    Base.metadata.drop_all(bind=engine)
    init_db()
    return {"detail": "db reset"}


@router.get("/users", response_model=List[user_schemas.StudentRead])
def list_users(current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(user_model.Student).all()


@router.post("/assign")
def assign_task_to_student(student_id: int, task_id: int, current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(user_model.Student).filter(user_model.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    task = db.query(task_model.Task).filter(task_model.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    st = st_model.StudentTask(student_id=student_id, task_id=task_id)
    db.add(st)
    db.commit()
    db.refresh(st)
    return {"detail": "assigned", "id": st.id}
