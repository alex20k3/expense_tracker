from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, groups, expenses, karma

app = FastAPI()

# 🚨 ВАЖНО: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://expense-tracker-1-fsn3.onrender.com",  # фронт
        "http://localhost:5173",                        # локалка
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(karma.router)


@app.get("/")
def root():
    return {"message": "Expense tracker API works"}
