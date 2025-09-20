from sqlalchemy.orm import Session
from typing import List
from ..schemas.movie import Movie
from .collaborative import get_collaborative_recommendations
from .content_based import get_content_based_recommendations


def get_hybrid_recommendations(db: Session, user_id: int, limit: int = 10) -> List[Movie]:
    """Get hybrid recommendations combining collaborative and content-based filtering."""
    try:
        # Get recommendations from both methods
        collaborative_recs = get_collaborative_recommendations(db, user_id, limit * 2)
        content_based_recs = get_content_based_recommendations(db, user_id, limit * 2)
        
        # Create movie ID sets for easy lookup
        collaborative_ids = set([movie.id for movie in collaborative_recs])
        content_based_ids = set([movie.id for movie in content_based_recs])
        
        # Combine recommendations with weights
        hybrid_movies = {}
        
        # Add collaborative recommendations with weight 0.6
        for i, movie in enumerate(collaborative_recs):
            score = 0.6 * (1.0 - i / len(collaborative_recs))  # Decreasing score
            hybrid_movies[movie.id] = {
                'movie': movie,
                'score': score,
                'source': 'collaborative'
            }
        
        # Add content-based recommendations with weight 0.4
        for i, movie in enumerate(content_based_recs):
            score = 0.4 * (1.0 - i / len(content_based_recs))  # Decreasing score
            if movie.id in hybrid_movies:
                # If movie appears in both, combine scores
                hybrid_movies[movie.id]['score'] += score
                hybrid_movies[movie.id]['source'] = 'hybrid'
            else:
                hybrid_movies[movie.id] = {
                    'movie': movie,
                    'score': score,
                    'source': 'content_based'
                }
        
        # Sort by combined score and return top recommendations
        sorted_movies = sorted(
            hybrid_movies.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return [item['movie'] for item in sorted_movies[:limit]]
    
    except Exception as e:
        print(f"Error in hybrid recommendations: {e}")
        # Fallback to collaborative filtering
        return get_collaborative_recommendations(db, user_id, limit)
