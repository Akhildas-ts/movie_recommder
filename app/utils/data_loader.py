from sqlalchemy.orm import Session
from typing import List
import random
from ..models.movie import Movie
from ..models.user import User
from ..models.rating import Rating
from ..core.security import get_password_hash


def load_sample_movies(db: Session) -> List[Movie]:
    """Load sample movies into the database."""
    sample_movies = [
        {
            "title": "The Shawshank Redemption",
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "genre": "Drama",
            "director": "Frank Darabont",
            "year": 1994,
            "duration": 142
        },
        {
            "title": "The Godfather",
            "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "genre": "Crime",
            "director": "Francis Ford Coppola",
            "year": 1972,
            "duration": 175
        },
        {
            "title": "The Dark Knight",
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "genre": "Action",
            "director": "Christopher Nolan",
            "year": 2008,
            "duration": 152
        },
        {
            "title": "Pulp Fiction",
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "genre": "Crime",
            "director": "Quentin Tarantino",
            "year": 1994,
            "duration": 154
        },
        {
            "title": "Forrest Gump",
            "description": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
            "genre": "Drama",
            "director": "Robert Zemeckis",
            "year": 1994,
            "duration": 142
        },
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "genre": "Sci-Fi",
            "director": "Christopher Nolan",
            "year": 2010,
            "duration": 148
        },
        {
            "title": "The Matrix",
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "genre": "Sci-Fi",
            "director": "Lana Wachowski",
            "year": 1999,
            "duration": 136
        },
        {
            "title": "Goodfellas",
            "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito.",
            "genre": "Crime",
            "director": "Martin Scorsese",
            "year": 1990,
            "duration": 146
        },
        {
            "title": "The Lord of the Rings: The Fellowship of the Ring",
            "description": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.",
            "genre": "Fantasy",
            "director": "Peter Jackson",
            "year": 2001,
            "duration": 178
        },
        {
            "title": "Fight Club",
            "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
            "genre": "Drama",
            "director": "David Fincher",
            "year": 1999,
            "duration": 139
        }
    ]
    
    created_movies = []
    for movie_data in sample_movies:
        # Check if movie already exists
        existing_movie = db.query(Movie).filter(Movie.title == movie_data["title"]).first()
        if not existing_movie:
            movie = Movie(**movie_data)
            db.add(movie)
            created_movies.append(movie)
    
    db.commit()
    return created_movies


def load_sample_users(db: Session) -> List[User]:
    """Load sample users into the database."""
    sample_users = [
        {"email": "alice@example.com", "username": "alice", "password": "password123"},
        {"email": "bob@example.com", "username": "bob", "password": "password123"},
        {"email": "charlie@example.com", "username": "charlie", "password": "password123"},
        {"email": "diana@example.com", "username": "diana", "password": "password123"},
        {"email": "eve@example.com", "username": "eve", "password": "password123"},
    ]
    
    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"])
            )
            db.add(user)
            created_users.append(user)
    
    db.commit()
    return created_users


def load_sample_ratings(db: Session) -> List[Rating]:
    """Load sample ratings into the database."""
    # Get all users and movies
    users = db.query(User).all()
    movies = db.query(Movie).all()
    
    if not users or not movies:
        return []
    
    created_ratings = []
    
    # Generate random ratings for each user
    for user in users:
        # Each user rates 3-7 random movies
        num_ratings = random.randint(3, 7)
        rated_movies = random.sample(movies, min(num_ratings, len(movies)))
        
        for movie in rated_movies:
            # Check if rating already exists
            existing_rating = db.query(Rating).filter(
                Rating.user_id == user.id,
                Rating.movie_id == movie.id
            ).first()
            
            if not existing_rating:
                rating_value = round(random.uniform(2.0, 5.0), 1)
                rating = Rating(
                    user_id=user.id,
                    movie_id=movie.id,
                    rating=rating_value,
                    review=f"Sample review for {movie.title}"
                )
                db.add(rating)
                created_ratings.append(rating)
    
    db.commit()
    return created_ratings


def load_all_sample_data(db: Session):
    """Load all sample data into the database."""
    print("Loading sample movies...")
    movies = load_sample_movies(db)
    print(f"Loaded {len(movies)} movies")
    
    print("Loading sample users...")
    users = load_sample_users(db)
    print(f"Loaded {len(users)} users")
    
    print("Loading sample ratings...")
    ratings = load_sample_ratings(db)
    print(f"Loaded {len(ratings)} ratings")
    
    return {"movies": movies, "users": users, "ratings": ratings}
