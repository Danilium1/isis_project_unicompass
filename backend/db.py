from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
import importlib

SQLALCHEMY_DATABASE_URL = "sqlite:///./unicompass.db"

# Needed for SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


# Create tables (imports of models will register them with Base)
def init_db():
	# Import model modules explicitly so all mappers are registered before first query.
	importlib.import_module("backend.user.model")
	importlib.import_module("backend.task.model")
	importlib.import_module("backend.student_task.model")
	configure_mappers()

	Base.metadata.create_all(bind=engine)

	# create default admin user if missing
	from backend.user import model as user_model

	db = SessionLocal()
	try:
		admin = db.query(user_model.Student).filter(user_model.Student.email == "admin@gmail.com").first()
		if not admin:
			admin_user = user_model.Student(
				first_name="Admin",
				last_name="User",
				email="admin@gmail.com",
				password="123123",
				is_admin=True,
			)
			db.add(admin_user)
			db.commit()
	finally:
		db.close()
