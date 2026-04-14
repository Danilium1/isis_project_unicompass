from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import engine, Base, init_db, get_db
from backend.user import model as user_model, schemas as user_schemas
from backend.task import model as task_model
from backend.student_task import model as st_model
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


@router.get("/student-tasks")
def student_tasks_report(current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin matrix: each student and each task with completion status."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    students = (
        db.query(user_model.Student)
        .filter(user_model.Student.is_admin == False)
        .order_by(user_model.Student.id)
        .all()
    )
    tasks = db.query(task_model.Task).order_by(task_model.Task.id).all()
    assignments = db.query(st_model.StudentTask).all()

    assignment_map = {(row.student_id, row.task_id): row for row in assignments}
    rows = []

    for student in students:
        for task in tasks:
            assignment = assignment_map.get((student.id, task.id))
            is_completed = bool(
                assignment
                and (
                    assignment.completed_at is not None
                    or (assignment.status or "").lower() == "completed"
                )
            )

            if assignment is None:
                status = "not assigned"
            elif is_completed:
                status = "completed"
            else:
                status = assignment.status or "not completed"

            rows.append(
                {
                    "student_id": student.id,
                    "student_name": f"{student.first_name} {student.last_name}".strip(),
                    "student_email": student.email,
                    "task_id": task.id,
                    "task_title": task.title,
                    "status": status,
                    "is_completed": is_completed,
                    "completed_at": assignment.completed_at.isoformat() if assignment and assignment.completed_at else None,
                }
            )

    return rows
