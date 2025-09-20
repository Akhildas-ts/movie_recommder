from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...crud.movie import (
    get_movie, get_movies, get_movies_by_genre, search_movies,
    get_movies_by_year, get_top_rated_movies, create_movie, update_movie, delete_movie
)
from ...schemas.movie import Movie, MovieCreate, MovieUpdate, MovieSearch
from ...api.deps import get_current_active_user, get_optional_current_user
from ...models.user import User

router = APIRouter()


@router.get("/", response_model=List[Movie])
def read_movies(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db)
):
    """Get list of movies."""
    movies = get_movies(db, skip=skip, limit=limit)
    return movies


@router.get("/top-rated", response_model=List[Movie])
def read_top_rated_movies(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Get top rated movies."""
    movies = get_top_rated_movies(db, limit=limit)
    return movies


@router.get("/search", response_model=List[Movie])
def search_movies_endpoint(
    query: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Search movies by title, description, or director."""
    movies = search_movies(db, query=query, skip=skip, limit=limit)
    return movies


@router.get("/genre/{genre}", response_model=List[Movie])
def read_movies_by_genre(
    genre: str,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Get movies by genre."""
    movies = get_movies_by_genre(db, genre=genre, skip=skip, limit=limit)
    return movies


@router.get("/year/{year}", response_model=List[Movie])
def read_movies_by_year(
    year: int,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Get movies by year."""
    movies = get_movies_by_year(db, year=year, skip=skip, limit=limit)
    return movies


@router.get("/{movie_id}", response_model=Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie by ID."""
    movie = get_movie(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=Movie)
def create_movie_endpoint(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new movie (admin only)."""
    return create_movie(db=db, movie=movie)


@router.put("/{movie_id}", response_model=Movie)
def update_movie_endpoint(
    movie_id: int,
    movie_update: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a movie (admin only)."""
    movie = update_movie(db, movie_id=movie_id, movie_update=movie_update)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.delete("/{movie_id}")
def delete_movie_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a movie (admin only)."""
    success = delete_movie(db, movie_id=movie_id)
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}
