from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import users, groups, expenses, karma   # <-- ВОТ ТАК

app = FastAPI(title="Shared Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для MVP, потом можно сузить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(karma.router, prefix="/api")
