from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "Movie Recommender API"
    debug: bool = False
    version: str = "1.0.0"
    
    # Database settings
    database_url: str = "sqlite:///./movie_recommender.db"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # ML settings
    model_path: str = "./models/"
    min_ratings_per_user: int = 5
    min_ratings_per_movie: int = 3
    
    class Config:
        env_file = ".env"


settings = Settings()
