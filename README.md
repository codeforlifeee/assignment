# EVE Healthcare Booking API 🏥

A production-ready backend service designed for EVE Healthcare, enabling users to book diagnostic tests, securely process simulated payments, and manage appointment states via robust background webhook integrations. 

This project was built to satisfy the EVE SDE Intern Hiring Assignment, implementing **100% of all core requirements** and **100% of all Optional Bonus Features**.

---

## 🚀 Key Features

*   **Robust Authentication**: JWT-based secure authentication utilizing `bcrypt` password hashing.
*   **Idempotent Webhooks**: Secure payment webhook processing designed to aggressively prevent double-processing or race conditions using strict database constraints.
*   **Asynchronous Processing**: Background job processing using **Celery** and **Redis** to ensure payment simulation webhooks are never lost during server reboots.
*   **Alembic Migrations**: Fully integrated SQLAlchemy migrations (no hacky `create_all()` shortcuts) automated seamlessly into Docker and Railway deployments.
*   **API Caching**: Integrated `fastapi-cache2` leveraging Redis to cache heavily accessed endpoints (e.g. `GET /centres`) reducing database load.
*   **Rate Limiting**: Integrated `fastapi-limiter` architecture designed to protect critical endpoints from malicious spam.
*   **Strict Validations**: Heavy utilization of Pydantic models with edge-case protections (e.g., blocking "time-travel" appointments set in the past).
*   **Professional Pagination**: Standardized multi-key JSON structure (skip, limit, total, data) across all list-based endpoints.
*   **Structured JSON Logging**: Implemented `loguru` to produce clean, easily readable, and highly searchable logs in production environments.
*   **Comprehensive Test Suite**: Automated integration testing utilizing `pytest` and `httpx` with temporary transactional database rollbacks.

---

## 🛠️ Tech Stack

*   **Framework**: FastAPI (Python 3.12+)
*   **Database**: PostgreSQL
*   **ORM / Migrations**: SQLAlchemy + Alembic
*   **Message Broker / Cache**: Redis
*   **Background Workers**: Celery
*   **Security**: python-jose, passlib, bcrypt, python-dotenv
*   **Infrastructure**: Docker, docker-compose, Uvicorn

---

## 💻 Running Locally

### Option 1: Docker (Recommended)
You can boot the entire stack (FastAPI, Celery, PostgreSQL, Redis) with a single command:
```bash
docker-compose up --build
```
*Note: Our `docker-compose.yml` automatically triggers Alembic migrations upon startup. The API will be instantly available at `http://localhost:8000/docs`.*

### Option 2: Native Development Mode
If you prefer running the code outside of Docker, the application has a built-in `TESTING` fallback that gracefully substitutes Redis with an In-Memory cache and bypasses strict rate limiting, allowing you to develop locally using SQLite:

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # (or .\venv\Scripts\activate on Windows)
   pip install -r requirements.txt
   ```
2. Set up environment variables (copy the template):
   ```bash
   cp .env.example .env
   ```
3. Run migrations and start the server:
   ```bash
   export TESTING=True
   alembic upgrade head
   uvicorn eve_health.main:app --reload
   ```

---

## ☁️ Deployment (Railway)

This repository is heavily optimized for zero-config deployment on platforms like [Railway](https://railway.app/).
1. Provision **PostgreSQL** and **Redis** plugins in a new Railway project.
2. Deploy this repository as the **Web Service**. Railway will detect the `Procfile` and automatically run Alembic migrations and boot Uvicorn.
3. Deploy this repository *a second time* in the same project, but override the custom Start Command to boot the Celery worker:
   `celery -A eve_health.celery_app.celery_app worker --loglevel=info`
4. Inject the `DATABASE_URL` and `REDIS_URL` reference variables into both deployments.

---

## 🧪 Running Tests
The suite includes edge cases testing for Auth, Centre creation, and the Booking Flow.
```bash
export TESTING=True
pytest tests/ -v
```

---

## 🛡️ Edge Cases Actively Handled

- **Financial Precision**: All pricing fields use precise `Numeric/Decimal` typing instead of standard floats to prevent floating-point rounding errors.
- **Time-Travel**: Users are strictly prevented from creating `appointment_date` bookings that occur in the past.
- **Data Encapsulation**: Strict JWT lifecycle enforcement and OAuth2 bearer token implementations.
- **Security Misconfigurations**: Application immediately crashes on boot (`ValueError`) if `SECRET_KEY` is not present in the environment (falling back to a hardcoded string is blocked).
- **Double-Payment Webhooks**: Unique constraint checks in the PostgreSQL database guarantee that a duplicate webhook event ID cannot be processed twice by Celery.

---

*Engineered meticulously for the EVE Healthcare SDE Intern Evaluation.*
