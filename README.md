# Twitter-like Application

A web application that allows users to post tweets, share URLs, and interact with other users' content.

## Prerequisites

- Docker
- Docker Compose
- Git

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create environment files:

For development:
```bash
# Create .env.dev file
echo "FLASK_APP=manage.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev" > .env.dev
```

For production:
```bash
# Create .env.prod file
echo "FLASK_APP=manage.py
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod" > .env.prod

# Create .env.prod.db file
echo "POSTGRES_USER=hello_flask
POSTGRES_PASSWORD=hello_flask
POSTGRES_DB=hello_flask_prod" > .env.prod.db
```

## Running the Application

### Development Environment

1. Start the development environment:
```bash
docker-compose up --build
```

2. Load test data (optional):
```bash
# For a small dataset (recommended for development)
docker-compose exec db python3 /docker-entrypoint-initdb.d/load_test_data.py --rows 100

# For a large dataset
docker-compose exec db python3 /docker-entrypoint-initdb.d/load_test_data.py --rows 1000000
```

3. Access the application:
- Web application: http://localhost:3797

### Production Environment

1. Start the production environment:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

2. Load test data (optional):
```bash
# For a small dataset
docker-compose -f docker-compose.prod.yml exec db python3 /docker-entrypoint-initdb.d/load_test_data.py --rows 100

# For a large dataset
docker-compose -f docker-compose.prod.yml exec db python3 /docker-entrypoint-initdb.d/load_test_data.py --rows 1000000
```

3. Access the application:
- Web application: http://localhost:3798

## Database Schema

The application uses PostgreSQL with the following tables:

### Users
- Primary key: user_id
- Fields: username, email, created_at, last_login, is_active

### Tweets
- Primary key: tweet_id
- Fields: user_id (foreign key), content, created_at, likes_count, retweets_count

### URLs
- Primary key: url_id
- Fields: tweet_id (foreign key), url, created_at, is_valid, last_checked

## Stopping the Application

### Development Environment
```bash
docker-compose down
```

### Production Environment
```bash
docker-compose -f docker-compose.prod.yml down
```
