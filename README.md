# Project Name

A utility for managing user accounts in the application.

**Prerequisites**
- Python 3 is required.
- Using a Virtual Environment (venv) is mandatory.

**Setup and Installation**
- Create the virtual environment:
  - `python3 -m venv .venv`
- Activate the virtual environment:
  - macOS: `source .venv/bin/activate`
  - Windows : `.venv\Scripts\Activate.ps1`
- Install dependencies from requirements.txt:
  - `pip install -r requirements.txt`

**Dependencies**
- `flask`
- `requests`
- `pandas`
- `kagglehub`
- `python-dotenv`
- `cryptography`
- `sqlite3` 

**Running Tests**
- Ensure the virtual environment is active.
- Install test dependencies:
  - `pip install pytest pytest-cov`
- Run the test suite (from the project root):
  - `pytest`
  - `pytest -vv`
- If your environment needs an explicit module path:
  - Linux/macOS: `PYTHONPATH=. pytest`
  - Windows (PowerShell): `$env:PYTHONPATH='.'; pytest`

**Execution**
- Ensure the virtual environment is active.
- Launch the main application:
  - `python -m src.components.Backend.App`
