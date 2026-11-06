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
