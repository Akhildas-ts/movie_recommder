from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from ..models.movie import Movie
from ..schemas.movie import MovieCreate, MovieUpdate


def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    """Get movie by ID."""
    return db.query(Movie).filter(Movie.id == movie_id).first()


def get_movies(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple movies."""
    return db.query(Movie).offset(skip).limit(limit).all()


def get_movies_by_genre(db: Session, genre: str, skip: int = 0, limit: int = 100):
    """Get movies by genre."""
    return db.query(Movie).filter(Movie.genre == genre).offset(skip).limit(limit).all()


def search_movies(db: Session, query: str, skip: int = 0, limit: int = 100):
    """Search movies by title, description, or director."""
    return db.query(Movie).filter(
        or_(
            Movie.title.contains(query),
            Movie.description.contains(query),
            Movie.director.contains(query)
        )
    ).offset(skip).limit(limit).all()


def get_movies_by_year(db: Session, year: int, skip: int = 0, limit: int = 100):
    """Get movies by year."""
    return db.query(Movie).filter(Movie.year == year).offset(skip).limit(limit).all()


def get_top_rated_movies(db: Session, limit: int = 10):
    """Get top rated movies."""
    return db.query(Movie).filter(Movie.total_ratings > 0).order_by(Movie.average_rating.desc()).limit(limit).all()


def create_movie(db: Session, movie: MovieCreate) -> Movie:
    """Create a new movie."""
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie_update: MovieUpdate) -> Optional[Movie]:
    """Update movie information."""
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return None
    
    update_data = movie_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_movie, field, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, movie_id: int) -> bool:
    """Delete a movie."""
    db_movie = get_movie(db, movie_id)
    if not db_movie:
        return False
    
    db.delete(db_movie)
    db.commit()
    return True


def update_movie_rating_stats(db: Session, movie_id: int):
    """Update movie's average rating and total ratings count."""
    from ..models.rating import Rating
    from sqlalchemy import func
    
    stats = db.query(
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('total_ratings')
    ).filter(Rating.movie_id == movie_id).first()
    
    db_movie = get_movie(db, movie_id)
    if db_movie:
        db_movie.average_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
        db_movie.total_ratings = stats.total_ratings or 0
        db.commit()
        db.refresh(db_movie)
        return db_movie
    return None
