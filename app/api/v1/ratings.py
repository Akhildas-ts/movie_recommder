from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...crud.rating import (
    get_rating, get_user_rating_for_movie, get_user_ratings,
    get_movie_ratings, get_ratings, create_rating, update_rating, delete_rating
)
from ...schemas.rating import Rating, RatingCreate, RatingUpdate, RatingWithMovie
from ...api.deps import get_current_active_user
from ...models.user import User

router = APIRouter()


@router.get("/", response_model=List[Rating])
def read_ratings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of ratings."""
    ratings = get_ratings(db, skip=skip, limit=limit)
    return ratings


@router.get("/my-ratings", response_model=List[RatingWithMovie])
def read_my_ratings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's ratings."""
    ratings = get_user_ratings(db, user_id=current_user.id, skip=skip, limit=limit)
    return ratings


@router.get("/movie/{movie_id}", response_model=List[Rating])
def read_movie_ratings(
    movie_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get ratings for a specific movie."""
    ratings = get_movie_ratings(db, movie_id=movie_id, skip=skip, limit=limit)
    return ratings


@router.get("/{rating_id}", response_model=Rating)
def read_rating(
    rating_id: int,
    db: Session = Depends(get_db)
):
    """Get rating by ID."""
    rating = get_rating(db, rating_id=rating_id)
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@router.post("/", response_model=Rating)
def create_rating_endpoint(
    rating: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new rating."""
    # Check if user already rated this movie
    existing_rating = get_user_rating_for_movie(db, current_user.id, rating.movie_id)
    if existing_rating:
        raise HTTPException(
            status_code=400,
            detail="You have already rated this movie. Use PUT to update your rating."
        )
    
    # Add user_id to the rating
    rating_data = rating.dict()
    rating_data["user_id"] = current_user.id
    
    return create_rating(db=db, rating=RatingCreate(**rating_data))


@router.put("/{rating_id}", response_model=Rating)
def update_rating_endpoint(
    rating_id: int,
    rating_update: RatingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a rating."""
    # Check if rating exists and belongs to current user
    existing_rating = get_rating(db, rating_id=rating_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    if existing_rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    rating = update_rating(db, rating_id=rating_id, rating_update=rating_update)
    return rating


@router.delete("/{rating_id}")
def delete_rating_endpoint(
    rating_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a rating."""
    # Check if rating exists and belongs to current user
    existing_rating = get_rating(db, rating_id=rating_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    if existing_rating.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    success = delete_rating(db, rating_id=rating_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    return {"message": "Rating deleted successfully"}
