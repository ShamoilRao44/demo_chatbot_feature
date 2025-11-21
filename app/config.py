"""Configuration management for the application"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Shampostgres2344!@localhost:5432/restaurant_agent"
    )
    
    # LLM
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_timeout: int = 120
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
