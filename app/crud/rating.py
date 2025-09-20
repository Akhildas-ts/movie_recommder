from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from ..models.rating import Rating
from ..schemas.rating import RatingCreate, RatingUpdate


def get_rating(db: Session, rating_id: int) -> Optional[Rating]:
    """Get rating by ID."""
    return db.query(Rating).filter(Rating.id == rating_id).first()


def get_user_rating_for_movie(db: Session, user_id: int, movie_id: int) -> Optional[Rating]:
    """Get user's rating for a specific movie."""
    return db.query(Rating).filter(
        and_(Rating.user_id == user_id, Rating.movie_id == movie_id)
    ).first()


def get_user_ratings(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all ratings by a user."""
    return db.query(Rating).filter(Rating.user_id == user_id).offset(skip).limit(limit).all()


def get_movie_ratings(db: Session, movie_id: int, skip: int = 0, limit: int = 100):
    """Get all ratings for a movie."""
    return db.query(Rating).filter(Rating.movie_id == movie_id).offset(skip).limit(limit).all()


def get_ratings(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple ratings."""
    return db.query(Rating).offset(skip).limit(limit).all()


def create_rating(db: Session, rating: RatingCreate) -> Rating:
    """Create a new rating."""
    db_rating = Rating(**rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    # Update movie rating stats
    from .movie import update_movie_rating_stats
    update_movie_rating_stats(db, rating.movie_id)
    
    return db_rating


def update_rating(db: Session, rating_id: int, rating_update: RatingUpdate) -> Optional[Rating]:
    """Update a rating."""
    db_rating = get_rating(db, rating_id)
    if not db_rating:
        return None
    
    update_data = rating_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rating, field, value)
    
    db.commit()
    db.refresh(db_rating)
    
    # Update movie rating stats
    from .movie import update_movie_rating_stats
    update_movie_rating_stats(db, db_rating.movie_id)
    
    return db_rating


def delete_rating(db: Session, rating_id: int) -> bool:
    """Delete a rating."""
    db_rating = get_rating(db, rating_id)
    if not db_rating:
        return False
    
    movie_id = db_rating.movie_id
    db.delete(db_rating)
    db.commit()
    
    # Update movie rating stats
    from .movie import update_movie_rating_stats
    update_movie_rating_stats(db, movie_id)
    
    return True


def get_ratings_for_collaborative_filtering(db: Session, min_ratings_per_user: int = 5):
    """Get ratings data for collaborative filtering."""
    from sqlalchemy import func
    
    # Get users with minimum ratings
    user_counts = db.query(Rating.user_id, func.count(Rating.id).label('rating_count')).group_by(Rating.user_id).having(func.count(Rating.id) >= min_ratings_per_user).subquery()
    
    # Get ratings for these users
    return db.query(Rating).join(user_counts, Rating.user_id == user_counts.c.user_id).all()
