from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routes import medicines, schedules, ocr, analysis, chat

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
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers (No Authentication Required)
app.include_router(medicines.router, prefix=f"{settings.api_v1_prefix}/medicines", tags=["Medicines"])
app.include_router(schedules.router, prefix=f"{settings.api_v1_prefix}/schedules", tags=["Schedules"])
app.include_router(ocr.router, prefix=f"{settings.api_v1_prefix}/ocr", tags=["OCR"])
app.include_router(analysis.router, prefix=f"{settings.api_v1_prefix}/analysis", tags=["Analysis"])
app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["AI Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
