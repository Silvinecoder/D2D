# Destination 2 Development

Destination 2 Development is a learning platform designed to provide high-quality professional courses. The platform empowers educators and care professionals by providing the tools and resources they need to learn at their own pace, develop their skills, and achieve certification with confidence.

---

# Project Structure
The application is organized as a monorepo containing two main applications:

``` bash
destination-2-development/
├── backend/
└── frontend/
```

## Backend

The backend is responsible for:

- API endpoints
- Business logic
- Database communication
- Authentication
- User management
- Application services

## Frontend

The frontend is responsible for:

- User interface
- Client-side application logic
- User interactions
- Communicating with the backend API

This monorepo structure allows both applications to be developed independently while keeping the entire project within a single repository.

---

# Backend Technology Stack

The backend runs inside Docker containers and uses the following technologies:

- **Python** – Main programming language.
- **FastAPI** – Framework used to build the REST API.
- **SQLAlchemy** – ORM used for database models and database communication.
- **Alembic** – Database migration management.
- **Docker** – Containerization for local development and deployment consistency.
- **uv** – Python package and environment management.

The backend follows a service-based architecture, separating:

- API routes
- Schemas
- Database models
- Business logic services
- Application configuration

This keeps the codebase maintainable, testable, and scalable.

---

# API Documentation

FastAPI automatically generates interactive API documentation using Swagger.

When running the backend locally, the documentation can be accessed at:

```bash
http://127.0.0.1:8000/docs
````

Swagger allows developers to:

* View available endpoints.
* Inspect request and response schemas.
* Test API requests directly from the browser.

---

# Authentication (Auth0)

The application uses Auth0 as the authentication and user registration provider.

Auth0 is responsible for:

* User registration.
* Password management.
* Email verification.
* Authentication.
* Identity management.

The application database does not create users directly through a registration endpoint.

Instead, after a user successfully authenticates through Auth0, the backend automatically creates or retrieves the corresponding local user record.

The database stores application-specific information such as:

* Account status.
* User roles.
* Profile information.
* Application permissions.

---

# Local Development

For a complete local development reset:

```bash
cd destination2development-backend

source .venv/bin/activate

docker compose down -v --remove-orphans

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

uv cache clean
uv sync

docker compose build --no-cache
docker compose up
```

## Database migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

---

## Code Formatting

Format the codebase using Ruff:

```bash
uv run ruff format
```

## Tests

Command to run e2e tests:

```bash
pytest tests/e2e

```


---

# Development Notes

* `uv` manages Python dependencies and virtual environments.
* Docker manages application and database containers.
* Alembic manages database schema changes.
* `__pycache__` directories and `.pyc` files are generated Python bytecode and should not be committed to version control.