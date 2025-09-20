from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.recommendation import (
    RecommendationRequest, RecommendationResponse,
    SimilarMoviesRequest, SimilarMoviesResponse
)
from ...schemas.movie import Movie
from ...api.deps import get_current_active_user
from ...models.user import User
from ...ml.hybrid import get_hybrid_recommendations
from ...ml.collaborative import get_collaborative_recommendations
from ...ml.content_based import get_content_based_recommendations, get_similar_movies

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get movie recommendations for a user."""
    # Verify user can only get recommendations for themselves
    if request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        if request.algorithm == "collaborative":
            recommendations = get_collaborative_recommendations(
                db, request.user_id, request.limit
            )
        elif request.algorithm == "content_based":
            recommendations = get_content_based_recommendations(
                db, request.user_id, request.limit
            )
        elif request.algorithm == "hybrid":
            recommendations = get_hybrid_recommendations(
                db, request.user_id, request.limit
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid algorithm. Choose from: collaborative, content_based, hybrid"
            )
        
        return RecommendationResponse(
            user_id=request.user_id,
            algorithm=request.algorithm,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/similar", response_model=SimilarMoviesResponse)
def get_similar_movies_endpoint(
    request: SimilarMoviesRequest,
    db: Session = Depends(get_db)
):
    """Get movies similar to a given movie."""
    try:
        similar_movies = get_similar_movies(db, request.movie_id, request.limit)
        return SimilarMoviesResponse(
            movie_id=request.movie_id,
            similar_movies=similar_movies
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar movies: {str(e)}")


@router.get("/trending", response_model=List[Movie])
def get_trending_movies(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending movies based on recent ratings."""
    from ...crud.movie import get_top_rated_movies
    return get_top_rated_movies(db, limit=limit)
