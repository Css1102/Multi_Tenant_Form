from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine
from .models import SQLModel
from .tenant_migration import normalize_tenants
from sqlmodel import Session
from fastapi.middleware.cors import CORSMiddleware
from .routers import forms, auth, files, analytics, submissions, exports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Lifespan event to create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    # Existing databases may contain tenant-name variants created before the
    # normalized-name rule was introduced.
    with Session(engine) as session:
        normalize_tenants(session)
    yield

app = FastAPI(title="Multi-Tenant Form Engine API", lifespan=lifespan)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "https://multi-tenant-form.vercel.app"

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(forms.router)
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(analytics.router)
app.include_router(submissions.router)
app.include_router(exports.router)
@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Form Engine API"}
