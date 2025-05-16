# Twitter-like Application
[![](https://github.com/eth8n/final_project_csci143/workflows/test.yml/badge.svg)](https://github.com/eth8n/final_project_csci143/test.yml/actions?query=workflow%3Atests)

A web application that allows users to create accounts, post messages (tweets), and search through content. The application is built with Flask and PostgreSQL.

## Features

- User authentication (login, logout, account creation)
- Post messages with a 280 character limit
- Browse messages on the home page with pagination
- Full-text search functionality with highlighted results
- Responsive web design

## Prerequisites

- Docker
- Docker Compose
- Git

## Getting Started

1. Clone the repository:
```bash
git clone <https://github.com/eth8n/final_project_csci143.git>
cd <rhttps://github.com/eth8n/final_project_csci143.git>
```

2. Create environment files:

For development:
```bash
# Create .env.dev file
echo "FLASK_APP=project/__init__.py
FLASK_DEBUG=1
DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres
APP_FOLDER=/usr/src/app" > .env.dev
```

## Connecting to Server

### Development Environment

1. Start the development environment:
```bash
docker-compose up --build
```
2. Add test data to database (if first time running)
```bash
docker-compose exec db python3 /scripts/load_test_data.py
```

3. Access the application:
- Web application: http://localhost:3797

## Database

The application uses PostgreSQL with the following tables:

### Users
- Stores user account information (username, email, password hash)
- Tracks account creation and last login times
- Enables user authentication

### Tweets
- Stores user messages with content limited to 280 characters
- Tracks creation time, likes, and retweets
- Supports full-text search using PostgreSQL's RUM extension

### URLs
- Extracts and stores URLs mentioned in tweets
- Tracks URL validity and when it was last checked

## Stopping the Application

### Development Environment
```bash
docker-compose down
```

### Production Environment
```bash
docker-compose -f docker-compose.prod.yml down
```
