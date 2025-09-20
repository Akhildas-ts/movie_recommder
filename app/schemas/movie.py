from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None


class MovieInDB(MovieBase):
    id: int
    average_rating: float
    total_ratings: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Movie(MovieInDB):
    pass


class MovieSearch(BaseModel):
    query: str
    genre: Optional[str] = None
    year: Optional[int] = None
    limit: int = 10
