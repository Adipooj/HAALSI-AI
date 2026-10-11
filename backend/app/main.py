from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1 import auth, participants, assessments, dashboard
from backend.app.db.session import engine, Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    description="HAALSI AI - Longitudinal Geriatric Decision Support & Frailty Assessment API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database table creation on startup
@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(participants.router, prefix=f"{settings.API_V1_STR}/participants", tags=["Participants"])
app.include_router(assessments.router, prefix=f"{settings.API_V1_STR}/assessments", tags=["Assessments"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])

@app.get("/health")
async def health_check():
    from backend.app.ml.inference_service import ml_service
    return {
        "status": "online",
        "database": "connected",
        "models_loaded": ml_service.loaded,
        "deployment_mode": settings.DEPLOYMENT_MODE,
        "version": "1.0.0"
    }
