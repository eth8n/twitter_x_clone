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

## Data Persistence

- Development data is stored in the `postgres_data` volume
- Production data is stored in the `postgres_data_prod` volume
- Data persists between container restarts

## Testing

The project includes GitHub Actions workflows that:
1. Build the containers
2. Start the services
3. Load test data
4. Verify the application is running correctly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Image Upload

---
Below is an example showing the web application uploading an image

![Uploading Image](testing_screenrecording.gif)

---

## Build Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/eth8n/flask-on-docker.git
cd flask-on-docker
```

### 2. Build and Run the Containers

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py create_db
```



### 3. Verify

Using the `docker ps` command to view all active docker processes actively running, expected output should be similar to:

```
CONTAINER ID   IMAGE                   COMMAND                  PORTS                                     NAMES
############   flask-on-docker-web     "/home/app/web/entry…"   5000/tcp                                  flask-on-docker-web-1
############   postgres:13             "docker-entrypoint.s…"   5432/tcp                                  flask-on-docker-db-1
############   flask-on-docker-nginx   "/docker-entrypoint.…"   0.0.0.0:3037->80/tcp, [::]:3037->80/tcp   flask-on-docker-nginx-1
```

### 4. Testing Application

**a) On a remote server, run:**

```bash
curl http://127.0.0.1:3037/
```

and 

```bash
curl http://127.0.0.1:3037/static/hello.txt
```
---
Expected outputs:

```json
{"hello": "world"}
```

and

```json
hi! App running
```

---
---

**b) Access Locally via SSH Port Forwarding**

Using another bash terminal on your local machine, run:

```bash
ssh <your.email>@lambda.compute.cmc.edu -p 5055 -L localhost:8080:127.0.0.1:3037
```

- View `http://localhost:8080/` on a browser

- `http://localhost:8080/upload` allows uploading of image/gif files to `http://localhost:8080/media/[filename]`
