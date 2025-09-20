from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.crud.movie import movie_crud, genre_crud
from app.schemas.movie import (
    MovieCreate, MovieUpdate, MovieList, MovieDetail, MovieSearchParams,
    GenreResponse, MovieStats
)
from app.api.deps import get_current_user_optional, get_pagination_params
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[MovieList])
async def get_movies(
    skip: int = 0,
    limit: int = 20,
    query: Optional[str] = Query(None, description="Search query"),
    genres: Optional[str] = Query(None, description="Comma-separated genre names"),
    min_year: Optional[int] = Query(None, description="Minimum release year"),
    max_year: Optional[int] = Query(None, description="Maximum release year"),
    min_rating: Optional[float] = Query(None, description="Minimum IMDb rating"),
    max_rating: Optional[float] = Query(None, description="Maximum IMDb rating"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get movies with optional filtering and search
    """
    # Build search parameters
    search_params = MovieSearchParams(
        query=query,
        genres=genres.split(",") if genres else None,
        min_year=min_year,
        max_year=max_year,
        min_rating=min_rating,
        max_rating=max_rating,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    movies = await movie_crud.get_multi(db, skip, limit, search_params)
    return movies


@router.get("/search", response_model=List[MovieList])
async def search_movies(
    q: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Search movies by title, description, etc.
    """
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    movies = await movie_crud.search_movies(db, q.strip(), skip, limit)
    return movies


@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(db: AsyncSession = Depends(get_db)):
    """
    Get all movie genres
    """
    genres = await genre_crud.get_all(db)
    return genres


@router.get("/genre/{genre_name}", response_model=List[MovieList])
async def get_movies_by_genre(
    genre_name: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get movies by genre
    """
    movies = await movie_crud.get_by_genre(db, genre_name, skip, limit)
    return movies


@router.get("/top-rated", response_model=List[MovieList])
async def get_top_rated_movies(
    limit: int = Query(20, le=100, description="Number of movies to return"),
    min_ratings: int = Query(5, description="Minimum number of ratings required"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top-rated movies
    """
    movies = await movie_crud.get_top_rated(db, min_ratings, limit)
    return movies


@router.get("/recent", response_model=List[MovieList])
async def get_recent_movies(
    limit: int = Query(20, le=100, description="Number of movies to return"),
    years_back: int = Query(2, description="How many years back to consider 'recent'"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recently released movies
    """
    movies = await movie_crud.get_recent_releases(db, years_back, limit)
    return movies


@router.get("/trending", response_model=List[MovieList])
async def get_trending_movies(
    limit: int = Query(20, le=100, description="Number of movies to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending movies (placeholder - could be based on recent ratings, views, etc.)
    """
    # For now, return recent highly-rated movies
    movies = await movie_crud.get_top_rated(db, min_ratings=3, limit=limit)
    return movies


@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get movie details by ID
    """
    movie = await movie_crud.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    return movie


@router.get("/{movie_id}/similar", response_model=List[MovieList])
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(10, le=50, description="Number of similar movies to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get movies similar to the specified movie
    """
    # Check if movie exists
    movie = await movie_crud.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    similar_movies = await movie_crud.get_similar_movies(db, movie_id, limit)
    return similar_movies


@router.post("/", response_model=MovieDetail, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_create: MovieCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new movie (for demo purposes - in production this would be admin-only)
    """
    movie = await movie_crud.create(db, movie_create)
    return movie


@router.put("/{movie_id}", response_model=MovieDetail)
async def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update movie (for demo purposes - in production this would be admin-only)
    """
    movie = await movie_crud.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    updated_movie = await movie_crud.update(db, movie_id, movie_update)
    return updated_movie


@router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete movie (for demo purposes - in production this would be admin-only)
    """
    success = await movie_crud.delete(db, movie_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return {"message": "Movie deleted successfully"}


@router.get("/{movie_id}/stats")
async def get_movie_stats(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get movie statistics (ratings, reviews, etc.)
    """
    movie = await movie_crud.get_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Import here to avoid circular imports
    from app.crud.rating import rating_crud
    stats = await rating_crud.get_movie_rating_stats(db, movie_id)
    
    return {
        "movie_id": movie_id,
        "title": movie.title,
        "release_year": movie.release_year,
        "total_ratings": stats["total_ratings"],
        "average_rating": stats["average_rating"],
        "rating_distribution": stats["rating_distribution"],
        "imdb_rating": movie.imdb_rating,
        "genres": [genre.name for genre in movie.genres],
        "runtime": movie.runtime_display
    }