# Quickstart: CRM MVP

Get the system running from a clean clone in under 5 minutes.

## 1. Clone and enter the project

```bash
git clone https://github.com/CristianMz21/crm.git
cd crm
```

## 2. Python and virtualenv

Python 3.11 or newer is required. The project is developed on 3.13.

```bash
python -m venv .venv
source .venv/bin/activate          # bash/zsh
# or:  .venv\Scripts\activate     # Windows
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Migrate the database

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) and applies all
migrations, including the data migration that seeds the default
4-stage pipeline.

## 5. Create the owner account

```bash
python manage.py createsuperuser
```

Follow the prompts. This is the user that authenticates against the
API and the admin. In v1 there is only one user.

## 6. (Optional) Seed fake data

```bash
python seed.py
```

This creates 50 clients, each with 1-4 contacts, 0-3 opportunities
across the pipeline stages, 0-5 activities, and 1-3 tags. Useful
for clicking around without typing.

## 7. Run the server

```bash
python manage.py runserver
```

Open:

- Admin: <http://127.0.0.1:8000/admin/>
- API: <http://127.0.0.1:8000/api/>
- Browsable API: same as above, the DRF UI is the default.

## 8. Run the tests

```bash
pytest
```

All tests should be green. The suite covers the API contract, the
audit log, the pipeline movement, the CSV export, and the
N+1 regression with `assertNumQueries`.

## What's where

| Path | What lives there |
|---|---|
| `config/` | Django project (settings, urls, wsgi) |
| `clientes/` | Clients, contacts, opportunities, activities, tags |
| `pipeline/` | Pipeline and stage models |
| `audit/` | Audit log model and signal |
| `dashboard/` | Dashboard endpoint and aggregations |
| `templates/` | Minimal HTML for the Django views |
| `seed.py` | Faker-based seeder |
| `.specify/memory/constitution.md` | The project's governing principles |
| `specs/001-crm-mvp/` | The MVP spec, plan, data model, tasks |
| `openspec/` | _Removed_. Replaced by `.specify/` + `specs/`. |

## Common gotchas

- **`AUTH` failures on the API**: the API requires the session
  cookie. If you are calling from curl, log in first or use a
  cookie jar.
- **Pipeline is empty**: the data migration seeds a default
  pipeline. If you deleted it, run `python manage.py shell` and
  call `pipeline.services.ensure_default_pipeline()`.
- **Audit log is huge**: it grows with every mutation. For
  development, you can `python manage.py flush` and re-migrate.
  In production this would be a retention policy concern (v2).
- **Migrations are out of date**: `python manage.py makemigrations`
  should be a no-op. If it isn't, you have a model change that
  hasn't been committed to the repo. Check `git diff clientes/models.py`.
- **The pipeline is wrong**: stages are ordered by `orden`. To
  insert a stage between two existing ones, set the new one's
  `orden` to a value between the neighbors. To re-order, swap the
  `orden` values. The unique constraint is `(pipeline, orden)`.
