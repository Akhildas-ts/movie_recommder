# Movie Recommender API

A comprehensive movie recommendation system built with FastAPI, featuring multiple recommendation algorithms including collaborative filtering, content-based filtering, and hybrid approaches.

## Features

- **User Authentication**: JWT-based authentication system
- **Movie Management**: CRUD operations for movies
- **Rating System**: Users can rate and review movies
- **Multiple Recommendation Algorithms**:
  - Collaborative Filtering (user-based)
  - Content-Based Filtering (movie features)
  - Hybrid Approach (combining both methods)
- **RESTful API**: Well-documented API endpoints
- **Database**: SQLAlchemy with SQLite (easily configurable for other databases)

## Project Structure

```
movie_recommender/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── security.py        # JWT auth
│   │   └── database.py        # DB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User SQLAlchemy model
│   │   ├── movie.py          # Movie models
│   │   └── rating.py         # Rating/Review models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # User Pydantic schemas
│   │   ├── movie.py          # Movie Pydantic schemas
│   │   ├── rating.py         # Rating Pydantic schemas
│   │   └── recommendation.py  # ML response schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py           # User database operations
│   │   ├── movie.py          # Movie CRUD
│   │   └── rating.py         # Rating operations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py           # Dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── movies.py     # Movie endpoints
│   │       ├── ratings.py    # Rating endpoints
│   │       └── recommendations.py # ML endpoints
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── collaborative.py  # Collaborative filtering
│   │   ├── content_based.py  # Content-based filtering
│   │   └── hybrid.py         # Hybrid recommendations
│   └── utils/
│       ├── __init__.py
│       └── data_loader.py    # Load sample movie data
├── tests/
├── requirements.txt
├── .env
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd movie_recommender
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Usage Examples

### Authentication

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "username": "user", "password": "password123"}'
```

2. Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user&password=password123"
```

### Movies

1. Get all movies:
```bash
curl -X GET "http://localhost:8000/api/v1/movies/"
```

2. Search movies:
```bash
curl -X GET "http://localhost:8000/api/v1/movies/search?query=action"
```

### Ratings

1. Rate a movie (requires authentication):
```bash
curl -X POST "http://localhost:8000/api/v1/ratings/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"movie_id": 1, "rating": 4.5, "review": "Great movie!"}'
```

### Recommendations

1. Get recommendations (requires authentication):
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "limit": 10, "algorithm": "hybrid"}'
```

## Recommendation Algorithms

### Collaborative Filtering
- Uses user-item rating matrix
- Finds similar users based on rating patterns
- Recommends movies liked by similar users
- Uses SVD for dimensionality reduction

### Content-Based Filtering
- Analyzes movie features (title, description, genre, director)
- Uses TF-IDF vectorization for text features
- Recommends movies similar to user's preferences
- Based on movie content similarity

### Hybrid Approach
- Combines collaborative and content-based methods
- Weighted combination of both approaches
- Provides more diverse and accurate recommendations

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `MIN_RATINGS_PER_USER`: Minimum ratings for collaborative filtering
- `MIN_RATINGS_PER_MOVIE`: Minimum ratings per movie

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
alembic upgrade head
```

### Loading Sample Data
The application includes sample data loading functionality in `app/utils/data_loader.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
# movie_recommder
