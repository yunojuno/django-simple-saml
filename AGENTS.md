# AGENTS.md

## Cursor Cloud specific instructions

This is `django-simple-saml`, a reusable Django library for managing multiple SAML Identity Providers via the database. It is **not** a standalone application — it's a library with a demo app for local testing.

### System dependencies

The `xmlsec` Python package requires native libraries. These must be installed at the OS level before `poetry install` will succeed:

```
xmlsec1 libxmlsec1-dev libxmlsec1-openssl libxml2-dev pkg-config
```

### Development commands

All commands use Poetry. See `tox.ini` for the canonical list. Quick reference:

| Task | Command |
|---|---|
| Install deps | `poetry install -E localhost` |
| Tests | `DJANGO_SECRET_KEY="test-key" poetry run pytest --cov=simple_saml --verbose tests/` |
| Formatting | `poetry run black --check simple_saml` |
| Linting | `ruff check simple_saml` (ruff is a tox dep, not a Poetry dev dep — install separately or use tox) |
| Type check | `poetry run mypy simple_saml` |
| Django checks | `poetry run python manage.py check --fail-level WARNING` |
| Migration check | `poetry run python manage.py makemigrations --dry-run --check` |
| Full CI matrix | `poetry run tox` |

### Gotchas

- `ruff` is **not** in `pyproject.toml` dev dependencies — it's only declared in `tox.ini`. Install it separately (`pip install ruff`) or run via `tox -e lint`.
- Django system checks (`manage.py check`) require the `localhost` extras (`-E localhost`) because the demo app settings reference `django-sslserver`.
- The `DJANGO_SECRET_KEY` env var must be set when running tests outside of tox (tox sets it automatically).
- Poetry creates the virtualenv in-project (`.venv/`) per `poetry.toml`.
