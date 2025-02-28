# Flask-on-Docker

## Overview

The repository is a fully containerized web application, integrating a **Flask** app served by **Gunicorn**, a **PostreSQL** database, and **Nginx** as a reverse proxy. The setup uses `docker compose` to orchestrate a multi-container environment, making it a straightforward blueprint for deploying a production-ready Flask application.

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
