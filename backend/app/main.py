from fastapi import FastAPI
from .db import Base, engine, SessionLocal
from . import models
from .routers import users, groups, expenses, karma
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

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

app.include_router(users.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(karma.router, prefix="/api")




@app.get("/")
def root():
    return {"message": "Expense tracker API works"}
