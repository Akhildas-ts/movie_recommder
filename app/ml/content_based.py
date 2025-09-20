from sqlalchemy.orm import Session
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..schemas.movie import Movie
from ..crud.movie import get_movie, get_movies
from ..crud.rating import get_user_ratings


def create_movie_features(db: Session):
    """Create TF-IDF features for movies based on title, description, genre, and director."""
    movies = get_movies(db)
    
    # Create text features for each movie
    movie_texts = []
    movie_ids = []
    
    for movie in movies:
        text_parts = []
        if movie.title:
            text_parts.append(movie.title)
        if movie.description:
            text_parts.append(movie.description)
        if movie.genre:
            text_parts.append(movie.genre)
        if movie.director:
            text_parts.append(movie.director)
        
        movie_text = " ".join(text_parts)
        movie_texts.append(movie_text)
        movie_ids.append(movie.id)
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(movie_texts)
    
    return tfidf_matrix, movie_ids, vectorizer


def get_content_based_recommendations(db: Session, user_id: int, limit: int = 10) -> List[Movie]:
    """Get content-based recommendations for a user."""
    try:
        # Get user's rated movies
        user_ratings = get_user_ratings(db, user_id)
        
        if not user_ratings:
            # User has no ratings, return popular movies
            from ..crud.movie import get_top_rated_movies
            return get_top_rated_movies(db, limit=limit)
        
        # Create movie features
        tfidf_matrix, movie_ids, vectorizer = create_movie_features(db)
        
        # Get user's preferences (weighted by rating)
        user_preferences = np.zeros(tfidf_matrix.shape[1])
        total_weight = 0
        
        for rating in user_ratings:
            if rating.movie_id in movie_ids:
                movie_idx = movie_ids.index(rating.movie_id)
                weight = rating.rating  # Use rating as weight
                user_preferences += weight * tfidf_matrix[movie_idx].toarray().flatten()
                total_weight += weight
        
        if total_weight > 0:
            user_preferences /= total_weight
        
        # Calculate similarities between user preferences and all movies
        similarities = cosine_similarity([user_preferences], tfidf_matrix)[0]
        
        # Get user's rated movie IDs
        rated_movie_ids = set([r.movie_id for r in user_ratings])
        
        # Find unrated movies with highest similarity
        movie_similarities = []
        for i, movie_id in enumerate(movie_ids):
            if movie_id not in rated_movie_ids:
                movie_similarities.append((movie_id, similarities[i]))
        
        # Sort by similarity and get top recommendations
        movie_similarities.sort(key=lambda x: x[1], reverse=True)
        recommended_movie_ids = [movie_id for movie_id, _ in movie_similarities[:limit]]
        
        # Get movie objects
        recommended_movies = []
        for movie_id in recommended_movie_ids:
            movie = get_movie(db, movie_id)
            if movie:
                recommended_movies.append(movie)
        
        return recommended_movies
    
    except Exception as e:
        print(f"Error in content-based filtering: {e}")
        # Fallback to popular movies
        from ..crud.movie import get_top_rated_movies
        return get_top_rated_movies(db, limit=limit)


def get_similar_movies(db: Session, movie_id: int, limit: int = 10) -> List[Movie]:
    """Get movies similar to a given movie."""
    try:
        # Create movie features
        tfidf_matrix, movie_ids, vectorizer = create_movie_features(db)
        
        if movie_id not in movie_ids:
            return []
        
        movie_idx = movie_ids.index(movie_id)
        movie_vector = tfidf_matrix[movie_idx]
        
        # Calculate similarities with all other movies
        similarities = cosine_similarity(movie_vector, tfidf_matrix)[0]
        
        # Get top similar movies (excluding the movie itself)
        movie_similarities = []
        for i, other_movie_id in enumerate(movie_ids):
            if other_movie_id != movie_id:
                movie_similarities.append((other_movie_id, similarities[i]))
        
        # Sort by similarity and get top recommendations
        movie_similarities.sort(key=lambda x: x[1], reverse=True)
        similar_movie_ids = [movie_id for movie_id, _ in movie_similarities[:limit]]
        
        # Get movie objects
        similar_movies = []
        for similar_movie_id in similar_movie_ids:
            movie = get_movie(db, similar_movie_id)
            if movie:
                similar_movies.append(movie)
        
        return similar_movies
    
    except Exception as e:
        print(f"Error finding similar movies: {e}")
        return []
