# Development setup

## Windows PowerShell

From the project root, verify Python 3.11 and create the local environment.

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check
```

If the launcher cannot find Python 3.11, install it with
`winget install --id Python.Python.3.11 -e` and reopen PowerShell. If `uv` is
available, `uv python install 3.11` and `uv venv --python 3.11 --seed .venv`
provide the same supported development environment.

If PowerShell blocks activation, invoke `.\.venv\Scripts\python.exe` in place
of `python` in the commands below. If imports fail, check
`python -m pip --version` for the environment path and rerun installation.

## Run and verify

```powershell
python -m streamlit run app.py
python -m pytest -v
python -m ruff check .
python -m ruff format --check .
python scripts/verify_setup.py
```

Run the verification commands in a separate terminal while the server is open,
or stop the server with Ctrl+C first. Open the local URL printed by Streamlit.

## Local and Community Cloud deployment

Use `app.py` as the Community Cloud entry point and select Python 3.11. The
runtime dependencies are pinned in `requirements.txt`. The development file
adds local verification tools. Treat cloud filesystem writes as temporary and
use console logging by default. Phase 1 starts without requiring data writes,
credentials, or access to OpenStreetMap.

## Phase 1 conventions

Overview serves as the home page. Native Streamlit navigation gives the seven
pages their approved titles. The immutable settings model and module constants
provide the metadata and experiment defaults. Importing them performs no
directory creation. Call `initialize_directories()` when data or result
directories are needed. Default file logging creates `logs/` on demand and
continues on the console if file access fails.

Downloaded and generated datasets belong under `data/raw/` and
`data/processed/`. Small offline samples belong under `data/samples/`.
