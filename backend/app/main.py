from fastapi import FastAPI
from .db import Base, engine, SessionLocal
from . import models
from .routers import users, groups, expenses, karma
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shared Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём таблицы
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(karma.router)


@app.get("/")
def root():
    return {"message": "Expense tracker API works"}
