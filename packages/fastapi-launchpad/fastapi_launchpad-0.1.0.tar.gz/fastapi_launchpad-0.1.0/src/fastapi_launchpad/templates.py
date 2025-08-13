from pathlib import Path
import inspect


def create_src_root(project_path: Path, project_name: str) -> None:
    """Create the main FastAPI application file."""

    src_content = inspect.cleandoc(f"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from src.routers.health import router as health_router

    app = FastAPI(
        title="{project_name or ''}",
        description="FastAPI project created with fastapi-launchpad",
        version="0.1.0",
    )

    # CORS middleware configuration, modify as per need
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Modify in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    """)

    app_dir = project_path / "src"
    app_dir.mkdir(parents=True, exist_ok=True)

    with open(app_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    with open(app_dir / "main.py", "w", encoding="utf-8") as f:
        f.write(src_content)


def create_requirements(project_path: Path, database: str) -> None:
    """Create requirements.txt with necessary dependencies."""
    database_name_map = {
        "postgres": "psycopg2-binary>=2.9.5",
        "mongodb": "motor>=3.7.0",
        "mysql": "mysqlclient>=2.2.0",
    }

    requirements = [
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "sqlalchemy>=2.0.0",
    ]
    db_req = database_name_map.get(database)
    if db_req:
        requirements.append(db_req)

    with open(project_path / "requirements.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))


def create_env_file(project_path: Path, database: str) -> None:
    """Create .env file with environment variables."""
    database_url_map = {
        "postgres": "postgresql://<user>:<password>@<host>/<db_name>",
        "mongodb": "mongodb+srv://<user>:<password>@<host>/<db_name>?retryWrites=true&w=majority",
        "mysql": "mysql://<user>:<password>@<host>/<db_name>",
    }

    env_vars = {
        "DEBUG": "True",
        "ENVIRONMENT": "development",
    }
    db_url = database_url_map.get(database)
    if db_url:
        env_vars.update({"DATABASE_URL": db_url})
    if database == "mongodb":
        env_vars.update({"MONGO_DATABASE_NAME": ""})

    with open(project_path / ".env", "w", encoding="utf-8") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    with open(project_path / ".env.example", "w", encoding="utf-8") as f:
        for key in env_vars.keys():
            f.write(f"{key}=\n")


def create_health_check(project_path: Path) -> None:
    """Create the healthcheck endpoint."""

    endpoint_content = inspect.cleandoc("""
    from fastapi import APIRouter, status
    from fastapi.responses import JSONResponse

    router = APIRouter()

    @router.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "Ok"}
        )
    """)

    app_dir = project_path / "src/routers"
    app_dir.mkdir(parents=True, exist_ok=True)

    with open(app_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write("")

    with open(app_dir / "health.py", "w", encoding="utf-8") as f:
        f.write(endpoint_content)


def create_db_config(project_path: Path, database: str) -> None:
    """Create database configuration file"""

    core_dir = project_path / "src"
    db_content = ""
    if database == "postgres" or database == "mysql":
        db_content = f"""from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    import os
    from dotenv import load_dotenv

    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    """

    elif database == "mongodb":
        db_content = """import motor.motor_asyncio
    from dotenv import load_dotenv
    import os

    load_dotenv()

    MONGODB_URL = os.getenv("DATABASE_URL")
    MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")

    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGO_DATABASE_NAME]
    """
    db_content = inspect.cleandoc(db_content)

    with open(core_dir / "database.py", "w", encoding="utf-8") as f:
        f.write(db_content)


def create_readme(project_path: Path, project_name: str | None) -> None:
    """Create README.md with instructions"""
    readme_content = inspect.cleandoc(f"""# {project_name if project_name else "##"}

    A FastAPI project created with fastapi-launchpad.

    ## Setup

    1. Create a virtual environment:
    ```bash
    python -m venv venv (use python3 if alias for python is defined on OS level)
    ```

    2. Activate the virtual environment:
    ```bash
    # On Windows:
    .\\venv\\Scripts\\activate
    # On Unix or MacOS:
    source venv/bin/activate
    ```

    3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    4. Update the database configuration (if applicable) in .env by replacing values
       for user, password and host accordingly

    5. Run the application:
    ```bash
    uvicorn src.main:app --reload
    ```

    6. Visit the documentation at http://127.0.0.1:8000/docs

    ## Project Structure

    ```
    {project_name + "/" if project_name else ""}
    ├── src/
    │   ├── dependencies/
    │   ├── models/
    │   ├── schemas/
    │   ├── routers/
    │   └── main.py
    ├── tests/
    ├── .env
    └── requirements.txt
    ```
    """)
    
    with open(project_path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)


def create_project_structure(
    project_path: Path,
    project_name: str | None,
    database: str | None,
) -> None:
    """Create the complete project structure."""

    directories = [
        "src/dependencies",
        "src/models",
        "src/schemas",
        "src/routers",
        "tests",
    ]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
        (project_path / directory / "__init__.py").touch()

    create_health_check(project_path)
    create_src_root(project_path, project_name)
    create_requirements(project_path, database)
    create_env_file(project_path, database)
    create_readme(project_path, project_name)

    if database:
        create_db_config(project_path, database)
