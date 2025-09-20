from sqlalchemy.orm import Session
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from ..schemas.movie import Movie
from ..crud.movie import get_movie
from ..crud.rating import get_ratings_for_collaborative_filtering, get_user_ratings


def create_user_movie_matrix(db: Session):
    """Create user-movie rating matrix."""
    ratings = get_ratings_for_collaborative_filtering(db)
    
    # Get unique users and movies
    users = list(set([r.user_id for r in ratings]))
    movies = list(set([r.movie_id for r in ratings]))
    
    # Create mapping
    user_to_idx = {user_id: idx for idx, user_id in enumerate(users)}
    movie_to_idx = {movie_id: idx for idx, movie_id in enumerate(movies)}
    
    # Create matrix
    matrix = np.zeros((len(users), len(movies)))
    
    for rating in ratings:
        user_idx = user_to_idx[rating.user_id]
        movie_idx = movie_to_idx[rating.movie_id]
        matrix[user_idx, movie_idx] = rating.rating
    
    return matrix, user_to_idx, movie_to_idx, users, movies


def get_collaborative_recommendations(db: Session, user_id: int, limit: int = 10) -> List[Movie]:
    """Get collaborative filtering recommendations for a user."""
    try:
        matrix, user_to_idx, movie_to_idx, users, movies = create_user_movie_matrix(db)
        
        if user_id not in user_to_idx:
            # User has no ratings, return popular movies
            from ..crud.movie import get_top_rated_movies
            return get_top_rated_movies(db, limit=limit)
        
        user_idx = user_to_idx[user_id]
        
        # Use SVD for dimensionality reduction
        svd = TruncatedSVD(n_components=min(50, min(matrix.shape) - 1))
        matrix_reduced = svd.fit_transform(matrix)
        
        # Calculate user similarities
        user_similarities = cosine_similarity([matrix_reduced[user_idx]], matrix_reduced)[0]
        
        # Get user's rated movies
        user_ratings = get_user_ratings(db, user_id)
        rated_movie_ids = set([r.movie_id for r in user_ratings])
        
        # Calculate predicted ratings for unrated movies
        predictions = []
        for movie_id in movies:
            if movie_id not in rated_movie_ids:
                movie_idx = movie_to_idx[movie_id]
                
                # Find similar users who rated this movie
                similar_users = []
                for other_user_idx, similarity in enumerate(user_similarities):
                    if other_user_idx != user_idx and matrix[other_user_idx, movie_idx] > 0:
                        similar_users.append((similarity, matrix[other_user_idx, movie_idx]))
                
                if similar_users:
                    # Weighted average of similar users' ratings
                    total_weight = sum([sim for sim, _ in similar_users])
                    if total_weight > 0:
                        predicted_rating = sum([sim * rating for sim, rating in similar_users]) / total_weight
                        predictions.append((movie_id, predicted_rating))
        
        # Sort by predicted rating and get top recommendations
        predictions.sort(key=lambda x: x[1], reverse=True)
        recommended_movie_ids = [movie_id for movie_id, _ in predictions[:limit]]
        
        # Get movie objects
        recommended_movies = []
        for movie_id in recommended_movie_ids:
            movie = get_movie(db, movie_id)
            if movie:
                recommended_movies.append(movie)
        
        return recommended_movies
    
    except Exception as e:
        print(f"Error in collaborative filtering: {e}")
        # Fallback to popular movies
        from ..crud.movie import get_top_rated_movies
        return get_top_rated_movies(db, limit=limit)
