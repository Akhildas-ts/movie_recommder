from pydantic import BaseModel
from typing import List, Optional
from .movie import Movie


class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10
    algorithm: str = "hybrid"  # collaborative, content_based, hybrid


class RecommendationResponse(BaseModel):
    user_id: int
    algorithm: str
    recommendations: List[Movie]
    confidence_scores: Optional[List[float]] = None


class SimilarMoviesRequest(BaseModel):
    movie_id: int
    limit: int = 10


class SimilarMoviesResponse(BaseModel):
    movie_id: int
    similar_movies: List[Movie]
    similarity_scores: Optional[List[float]] = None
