from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "PillMate"
    app_version: str = "1.0.0"
    debug: bool = True
    api_v1_prefix: str = "/api"
    
    # Database
    database_url: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "pillmate_db"
    db_user: str = "postgres"
    db_password: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    
    # OCR
    tesseract_cmd: str = "/usr/local/bin/tesseract"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # File Upload
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
