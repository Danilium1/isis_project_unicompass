from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class StudentBase(BaseModel):
	first_name: str = Field(..., max_length=100)
	last_name: str = Field(..., max_length=100)
	patronymic: Optional[str] = None
	citezenship: Optional[str] = None
	school: Optional[str] = None
	study_group: Optional[str] = None
	age: Optional[int] = None
	email: EmailStr


class StudentCreate(StudentBase):
	password: str = Field(..., min_length=6)


class MinimalStudentCreate(BaseModel):
	first_name: str = Field(..., max_length=100)
	last_name: str = Field(..., max_length=100)
	email: EmailStr
	password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class TokenResponse(BaseModel):
	token: str


class StudentRead(StudentBase):
	id: int
	is_admin: Optional[bool] = False

	class Config:
		orm_mode = True


class StudentUpdate(BaseModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	patronymic: Optional[str] = None
	citezenship: Optional[str] = None
	school: Optional[str] = None
	study_group: Optional[str] = None
	age: Optional[int] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None
