from typing import List

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.user import model as user_model, schemas as user_schemas


router = APIRouter(prefix="/user", tags=["user"])


def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")
    token = authorization.split(" ", 1)[1]
    user = db.query(user_model.Student).filter(user_model.Student.token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@router.post("/", response_model=user_schemas.StudentRead)
def create_user(student: user_schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(user_model.Student).filter(user_model.Student.email == student.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_student = user_model.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/register", response_model=user_schemas.StudentRead)
def register_user(payload: user_schemas.MinimalStudentCreate, db: Session = Depends(get_db)):
    existing = db.query(user_model.Student).filter(user_model.Student.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    data = payload.dict()
    db_student = user_model.Student(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        password=data.get("password"),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/login", response_model=user_schemas.TokenResponse)
def login(payload: user_schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(user_model.Student).filter(user_model.Student.email == payload.email).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid4())
    user.token = token
    db.add(user)
    db.commit()
    return {"token": token}


@router.post("/logout")
def logout(current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.token = None
    db.add(current_user)
    db.commit()
    return {"detail": "logged out"}


@router.get("/me", response_model=user_schemas.StudentRead)
def read_me(current_user: user_model.Student = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[user_schemas.StudentRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(user_model.Student).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=user_schemas.StudentRead)
def get_user(user_id: int, current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(user_model.Student).filter(user_model.Student.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=user_schemas.StudentRead)
def update_user(user_id: int, payload: user_schemas.StudentUpdate, current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(user_model.Student).filter(user_model.Student.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: user_model.Student = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(user_model.Student).filter(user_model.Student.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "deleted"}
