from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import users, groups, expenses, karma

app = FastAPI(title="Shared Expense Tracker")

# 👇 ВОТ ЗДЕСЬ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://expense-tracker-1-fsn3.onrender.com",  # фронт на Render
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём таблицы
Base.metadata.create_all(bind=engine)

# роутеры
app.include_router(users.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(karma.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Expense tracker API works"}
