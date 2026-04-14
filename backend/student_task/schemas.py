from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentTaskBase(BaseModel):
	student_id: Optional[int] = None
	task_id: int
	deadline: Optional[datetime] = None
	status: Optional[str] = None
	completed_at: Optional[datetime] = None


class StudentTaskCreate(StudentTaskBase):
	pass


class StudentTaskRead(StudentTaskBase):
	id: int

	class Config:
		orm_mode = True


class StudentTaskUpdate(BaseModel):
	deadline: Optional[datetime] = None
	status: Optional[str] = None
	completed_at: Optional[datetime] = None
