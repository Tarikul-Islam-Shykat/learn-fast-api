# learn-fast-api

## Setup

These instructions install FastAPI in a project-specific virtual environment so its packages stay separate from other Python projects. FastAPI's first-steps guide currently uses Python 3.10 or newer.

### Windows

Open PowerShell in the project folder and check that Python is installed:

```powershell
py --version
```

If `py` is not recognized, try `python --version`. If neither command works, install Python from [python.org](https://www.python.org/downloads/) and reopen PowerShell.

Create and activate a virtual environment, then install FastAPI:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "fastapi[standard]"
```

If `py` was not recognized but `python` worked, use `python -m venv .venv` for the first command instead.

### macOS

Open Terminal in the project folder and check that Python is installed:

```bash
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/) and reopen Terminal.

Create and activate a virtual environment, then install FastAPI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "fastapi[standard]"
```

### Verify the installation

With the virtual environment active, check the installed FastAPI version and location:

```bash
python -m pip show fastapi
```

The output should include the package name, version, and a location inside this project's `.venv` folder. The `(.venv)` prefix in your terminal prompt indicates that the environment is active. If you see a pip update notice, it is informational; updating pip is optional.

## Target Application Structure

As the project grows, organize code by feature. Add folders when we introduce the concepts they are responsible for; the early lessons can stay in `main.py` until we refactor them.

```text
app/
+-- main.py
+-- core/
|   +-- config.py
|   +-- errors.py
+-- db/
|   +-- session.py
+-- features/
    +-- users/
    |   +-- router.py
    |   +-- schemas.py
    |   +-- service.py
    |   +-- repository.py
    |   +-- models.py
    +-- tasks/
        +-- router.py
        +-- schemas.py
        +-- service.py
        +-- repository.py
        +-- models.py
```

The request flow through a feature is:

```text
router -> service -> repository -> database
```

- **`router.py`** defines HTTP routes, methods, parameters, and status codes.
- **`service.py`** contains feature rules and use cases, such as whether a user may update a task.
- **`repository.py`** contains database queries for that feature.
- **`schemas.py`** defines the data accepted by and returned from the API, usually with Pydantic models.
- **`models.py`** describes how the feature's data is stored in the database.
- **`db/session.py`** holds shared database connection and session setup.
- **`core/config.py`** holds application-wide settings; **`core/errors.py`** holds shared error handling.
- **`main.py`** creates the FastAPI application and connects the feature routers.

This is the structure to grow toward, not a requirement to create every file immediately. For example, `repository.py` and `models.py` become relevant when we add a database.

## Learning notes

- [Section 2: SQL databases and SQLAlchemy](documentation/learning-road-map/section-2-sql-database-notes.md)
