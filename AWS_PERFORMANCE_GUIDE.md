# Karya Siddhi - AWS Production Performance Guide (< 20ms Latency)

Achieving less than 10-20ms latency and handling massive concurrent traffic for the Karya Siddhi portal requires a robust, scalable AWS architecture. Django by itself running on the built-in `runserver` is single-threaded and not meant for production.

Follow these critical deployment steps to guarantee high performance with zero lag.

## 1. Application Server: Gunicorn & Uvicorn (ASGI)
Django must not run on `manage.py runserver` in production.
- **Action**: Use **Gunicorn** with **Uvicorn workers** (ASGI) to handle thousands of concurrent connections asynchronously.
- **Command Example**: 
  ```bash
  gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker --workers 4 --threads 2
  ```
- **Why**: Asynchronous workers prevent the server from blocking when waiting for a database query (like booking a Puja) to finish, keeping response times under 10ms.

## 2. Reverse Proxy: NGINX
Never expose Gunicorn directly to the internet.
- **Action**: Place **NGINX** in front of Gunicorn. NGINX is incredibly fast at serving static and media files.
- **Why**: It buffers requests, handles SSL/TLS termination, and serves your CSS, JS, and Images directly (meaning Django never has to waste CPU cycles rendering them).

## 3. Database Layer: Amazon RDS (PostgreSQL)
- **Action**: Migrate the local PostgreSQL database to **Amazon RDS (PostgreSQL)**.
- **Optimization**: Implement **PgBouncer** (Database Connection Pooling).
- **Why**: Django creates a new database connection for every request. PgBouncer keeps a pool of open connections, saving ~5-10ms per request.

## 4. In-Memory Caching: Redis (Amazon ElastiCache)
- **Action**: Configure Django to use **Redis** as its caching backend.
- **What to Cache**: 
  - The **SEO Metadata** (so it doesn't query the DB on every single page load).
  - **Puja Service Lists** and **Hero Configs**.
- **Django Configuration** (`settings.py`):
  ```python
  CACHES = {
      "default": {
          "BACKEND": "django.core.cache.backends.redis.RedisCache",
          "LOCATION": "redis://your-elasticache-endpoint:6379",
      }
  }
  ```
- **Why**: Grabbing an object from Redis takes < 1ms, compared to a ~10-15ms SQL query.

## 5. Global CDN: Amazon CloudFront
- **Action**: Serve all static files (`/static/`) and user-uploaded media (`/media/`) via **CloudFront** backed by an **S3 Bucket**.
- **Why**: CloudFront caches your heavy assets (like the 3D Hanuman video, background images, and CSS) in Edge Locations globally. If a user in Hyderabad loads the site, they get the assets from a server physically in Hyderabad, reducing load time from seconds to milliseconds.

## 6. Load Balancing: Application Load Balancer (ALB)
- **Action**: Put your EC2 instances (running NGINX+Gunicorn) behind an AWS Application Load Balancer.
- **Why**: If traffic spikes heavily (e.g., during a major festival), AWS Auto Scaling will spin up more EC2 instances, and the ALB will evenly distribute the thousands of requests, ensuring no single server gets overwhelmed.

## Summary Checklist for < 20ms Responses:
1. [ ] **Gunicorn + ASGI** (Handles concurrent Python logic).
2. [ ] **NGINX** (Reverse proxy).
3. [ ] **Redis / ElastiCache** (Caches database results).
4. [ ] **CloudFront + S3** (Caches images and video).
5. [ ] **RDS + PgBouncer** (Optimizes database writes/reads).
