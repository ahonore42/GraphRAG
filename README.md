# Neo4j GraphRAG API

![Project Version](https://img.shields.io/badge/version-0.1.0-blue)

This project provides a robust and scalable FastAPI application designed for a Neo4j GraphRAG solution. It emphasizes modern Python development practices, containerization with Docker, and automated continuous integration/continuous deployment (CI/CD) using GitHub Actions to ensure code quality, reliability, and efficient deployment.

## Table of Contents
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Application](#running-the-application)
  - [Development Mode (with Docker Compose)](#development-mode-with-docker-compose)
  - [Local API Only (without Docker)](#local-api-only-without-docker)
- [Configuration](#configuration)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [CI/CD Pipeline](#ci/cd-pipeline)
- [Stopping Services](#stopping-services)
- [Makefile Commands](#makefile-commands)

<details>
<summary>Project Structure</summary>

The project follows a structured layout to enhance maintainability and scalability:

```
/
├───.dockerignore
├───.env.example
├───.gitignore
├───docker-compose.yml
├───Dockerfile
├───Makefile
├───pyproject.toml
├───README.md
├───uv.lock
├───src/
│   ├───__init__.py         # Makes 'src' a Python package
│   ├───main.py             # Main FastAPI application instance, health check, and startup logic
│   ├───config.py           # Pydantic settings for the application
│   ├───api/                # API-related components
│   │   ├───__init__.py
│   │   └───routers/        # Contains FastAPI APIRouter instances
│   │       ├───__init__.py
│   │       └───health.py   # Example: health check router
│   ├───core/               # Core application components (e.g., database connections, dependencies)
│   │   ├───__init__.py
│   │   └───db/             # Database connection management
│   │       ├───__init__.py
│   │       └───connections.py # Consolidated database connection setup and health checks
│   ├───schemas/            # Pydantic models for request/response validation and serialization
│   │   ├───__init__.py
│   │   └───item.py         # Example: ItemCreate, ItemRead models
│   ├───services/           # Business logic, data manipulation, CRUD operations
│   │   ├───__init__.py
│   │   └───item.py         # Example: functions to interact with Item data
│   └───utils/              # General utility functions
│       └───__init__.py
├───tests/                  # Unit and integration tests
│   ├───__init__.py
│   ├───test_config.py      # Tests for configuration loading
│   └───test_main.py        # Tests for main application endpoints (e.g., health check)
├───.github/                # GitHub specific configurations
│   └───workflows/          # GitHub Actions workflow definitions
│       └───ci.yml          # Main CI/CD pipeline workflow
├───__pycache__/
├───.git/...
└───.venv/...
```
</details>

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker Desktop**: Includes Docker Engine and Docker Compose.
*   **make**: A build automation tool (usually pre-installed on Linux/macOS).
*   **uv**: A fast Python package installer and resolver. Follow the instructions on [uv's official website](https://astral.sh/uv) for installation.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd graphrag-neo4j-qdrant
    ```

2.  **Initialize Project Dependencies:**
    This command sets up the Python virtual environment and installs all necessary dependencies using `uv`.
    ```bash
    make init
    ```

## Running the Application

### Development Mode (with Docker Compose)

This is the recommended way to run the full application stack, including Neo4j, Qdrant, Redis, and the FastAPI API, all within Docker containers.

```bash
make dev
```

Once the services are up, you can access:
*   **Neo4j Browser:** `http://localhost:7474` (default credentials: `neo4j`/`password`)
*   **Qdrant:** `http://localhost:6333`
*   **Redis:** `localhost:6379`
*   **FastAPI API:** `http://localhost:8000`
*   **FastAPI API Docs:** `http://localhost:8000/docs`

### Local API Only (without Docker)

If you only want to run the FastAPI application locally (without the Dockerized databases), you can use:

```bash
make run
```

This will start the FastAPI server on `http://localhost:8000`. Note that this mode requires your local environment to have access to the necessary database services (Neo4j, Qdrant, Redis) if your API endpoints interact with them.

## Configuration

The application's configuration is managed via environment variables, loaded using `pydantic-settings`.

*   **`.env` file**: Create a `.env` file in the project root (you can copy `.env.example` as a starting point). This file allows you to override default settings for local development or specific deployments.
*   **`src/config.py`**: Defines all available settings and their default values. Environment variables take precedence over values in the `.env` file, and `.env` values take precedence over defaults in `src/config.py`.

Example `.env` (copy from `.env.example` and modify):
```
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Update these with your hosted service URLs for production
# NEO4J_URL=neo4j+s://your-instance.databases.neo4j.io
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=your-secure-password

# QDRANT_URL=https://your-cluster.qdrant.tech
# QDRANT_API_KEY=your-api-key

# REDIS_URL=redis://username:password@your-redis-host:port

# FRONTEND_DOMAIN=http://localhost:3000 # For CORS, if applicable
```

## Stopping Services

To stop and remove all running Docker containers and their associated volumes:

```bash
make clean
```

## Makefile Commands

For a full list of available `make` commands and their descriptions, run:

```bash
make help
```