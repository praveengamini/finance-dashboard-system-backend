from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.startup import check_db, init_db
from auth.router import router as auth_router
from records.router import router as records_router
from dashboard.router import router as dashboard_router
from users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db()
    await init_db()
    yield


app = FastAPI(
    title="Finance Dashboard API",
    description="Role-based finance data processing and access control backend.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(records_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Health"])
async def health():
    return {"status": "ok", "message": "Finance API is running"}