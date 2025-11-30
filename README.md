# IT-Ticket-Project

Simple IT ticketing sample app (Flask). This repository contains a small example web application
for creating, viewing, updating and deleting simple support tickets. The project is structured
so the app can be run locally, tested with pytest, and linted/scanned using pre-commit, ruff,
bandit and safety in CI.

Contents
- `ticketing_app.py` - Flask app entrypoint and routes wiring
- `IT Ticket Project/` (inner project) - main app code: models, services, routes, templates
- `tests/` - unit tests and helpers
- `.github/workflows/` - CI workflows for testing, linting, and security

Quick start (local)
1. Create and activate a Python venv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install runtime and dev deps (project uses local editable install):

```bash
python -m pip install --upgrade pip
# from repository root, install inner project editable and dev extras if provided
pip install -e "IT Ticket Project"[dev] || pip install -e "IT Ticket Project"
```

3. Run the app:

```bash
python3 ticketing_app.py
# open http://127.0.0.1:5000/ in your browser
```

Testing

- Run pytest from repo root (a top-level `pytest.ini` and `conftest.py` ensure tests discover the inner project):

```bash
python -m pytest -q
```

Developer tooling and CI

- This repo uses `pre-commit` (black, isort, ruff, etc.), `bandit` and `safety` for security scanning.
- A root-level GitHub Actions workflow runs tests, lint and security checks. If you change formatting
	or pre-commit hooks, run `pre-commit run --all-files` locally, fix and commit the results.

Notes / gotchas
- The inner project folder contains the app source and templates and is installed editable in CI so
	tests can be executed from the repo root.
- If CI fails on linting, ensure pre-commit hooks are run from the correct working directory (the workflow was updated
	to run pre-commit and ruff in the inner `IT Ticket Project` directory in check-only mode).

Contributing
- Open a branch, make a small, focused change, run tests and pre-commit locally, then create a PR.

License
- This repository is provided as a learning example; check the `LICENSE` file if present or add one.
