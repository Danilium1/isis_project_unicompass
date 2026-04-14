from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
	# import model modules so they register with Base before creating tables
	try:
		import backend.user.model  # noqa: F401
		import backend.task.model  # noqa: F401
		import backend.student_task.model  # noqa: F401
	except Exception:
		# if imports fail, proceed; create_all will still work for already-registered models
		pass

	Base.metadata.create_all(bind=engine)

	# create default admin user if missing
	try:
		from backend.user import model as user_model
		from sqlalchemy.orm import Session

		db = SessionLocal()
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
		db.close()
	except Exception:
		pass


# Auto-initialize DB on import (safe for development MVP)
init_db()
