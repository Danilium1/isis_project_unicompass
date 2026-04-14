from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.db import Base

class Task(Base):
	__tablename__ = "task"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(200), nullable=False)
	description = Column(Text, nullable=True)

	student_tasks = relationship(
		"StudentTask",
		back_populates="task",
		cascade="all, delete-orphan",
	)

	def __repr__(self):
		return f"<Task id={self.id} title={self.title}>"
