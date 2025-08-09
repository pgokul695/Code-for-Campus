from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .core.firebase import initialize_firebase
from .database import engine, Base
from .api import notices, users, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
origins = settings.BACKEND_CORS_ORIGINS
if not origins:
    origins = []

# Convert string to list if it's a string (for Railway environment variables)
if isinstance(origins, str):
    origins = [origin.strip() for origin in origins.split(",") if origin.strip()]

# Add production frontend URL to allowed origins
production_url = "https://code-for-campus-fe-production.up.railway.app"
if production_url not in origins:
    origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r'https?://(localhost|code-for-campus.*\.vercel\.app|code-for-campus.*\.railway\.app|code-for-campus-fe-production\.up\.railway\.app)',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(notices.router, prefix=f"{settings.API_V1_STR}/notices", tags=["notices"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Virtual Notice Board API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
