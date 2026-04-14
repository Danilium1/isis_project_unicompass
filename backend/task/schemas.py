from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
	title: str = Field(..., max_length=200)
	description: Optional[str] = None


class TaskCreate(TaskBase):
	pass


class TaskRead(TaskBase):
	id: int

	class Config:
		orm_mode = True
