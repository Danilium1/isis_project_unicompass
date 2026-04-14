from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.user import router as user_router
from backend.task import router as task_router
from backend.student_task import router as student_task_router
from backend.admin import router as admin_router

app = FastAPI(title="unicompass")

app.include_router(user_router)
app.include_router(task_router)
app.include_router(student_task_router)
app.include_router(admin_router)

# Serve frontend static files from the frontend/ directory at root
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")



