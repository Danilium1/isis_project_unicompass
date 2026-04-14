from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.db import Base


class Student(Base):
	__tablename__ = "student"

	id = Column(Integer, primary_key=True, index=True)
	first_name = Column(String(100), nullable=False)
	last_name = Column(String(100), nullable=False)
	patronymic = Column(String(100), nullable=True)
	citezenship = Column(String(100), nullable=True)
	school = Column(String(200), nullable=True)
	study_group = Column(String(100), nullable=True)
	age = Column(Integer, nullable=True)
	email = Column(String(256), unique=True, index=True, nullable=False)
	password = Column(String(256), nullable=False)
	token = Column(String(128), unique=True, index=True, nullable=True)
	is_admin = Column(Boolean, default=False, nullable=False)

	student_tasks = relationship(
		"StudentTask",
		back_populates="student",
		cascade="all, delete-orphan",
	)

	def __repr__(self):
		return f"<Student id={self.id} email={self.email} name={self.first_name} {self.last_name}>"
