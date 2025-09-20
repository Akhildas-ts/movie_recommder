from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingBase(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating between 1.0 and 5.0")
    review: Optional[str] = None


class RatingCreate(RatingBase):
    movie_id: int


class RatingUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    review: Optional[str] = None


class RatingInDB(RatingBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Rating(RatingInDB):
    pass


class RatingWithMovie(Rating):
    movie: dict  # Will be populated with movie details


class RatingWithUser(Rating):
    user: dict  # Will be populated with user details
