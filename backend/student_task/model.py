from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base


class StudentTask(Base):
	__tablename__ = "student_task"

	id = Column(Integer, primary_key=True, index=True)
	student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
	task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
	deadline = Column(DateTime, nullable=True)
	status = Column(String(50), nullable=True)
	completed_at = Column(DateTime, nullable=True)

	student = relationship("backend.user.model.Student", back_populates="student_tasks")
	task = relationship("backend.task.model.Task", back_populates="student_tasks")

	def __repr__(self):
		return f"<StudentTask id={self.id} student_id={self.student_id} task_id={self.task_id}>"
