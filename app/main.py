from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routes import medicines, schedules, ocr, analysis, chat, users

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="필메이트 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get(
    "/",
    tags=["시스템"],
    summary="API 상태",
)
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }

@app.get(
    "/health",
    tags=["시스템"],
    summary="서버 상태 체크",
)
async def health_check():
    return {"status": "healthy"}

# Include routers (No Authentication Required)
app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["사용자"])
app.include_router(medicines.router, prefix=f"{settings.api_v1_prefix}/medicines", tags=["약"])
app.include_router(schedules.router, prefix=f"{settings.api_v1_prefix}/schedules", tags=["스케쥴"])
app.include_router(ocr.router, prefix=f"{settings.api_v1_prefix}/ocr", tags=["OCR"])
app.include_router(analysis.router, prefix=f"{settings.api_v1_prefix}/analysis", tags=["분석"])
app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["AI 채팅"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
