# Automation Build & Test Tracker

A Django-based tracker for multi-team Build → Test → Deploy automation workflows, designed for Apple internship interview.

## Overview

- **Hierarchical model**: Organization → Team → Project → Pipeline → Stage → SubStage
- **JSON-configurable pipelines**: Define stages/substages, weights, and validation rules in JSON
- **Weighted scoring**: Each Run computes overall completion based on stage/substage weights
- **REST API**: Full CRUD + trend analysis endpoints via Django REST Framework
- **Auto-result creation**: Signals automatically create StageResult/SubStageResult rows on Run creation

## Quick Setup (macOS/zsh)

### 1. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
python manage.py makemigrations tracker
python manage.py migrate tracker
```

### 4. Create seed data (Organization/Team/Project)

```bash
python manage.py shell -c "
from tracker.models import Organization, Team, Project
org = Organization.objects.create(name='ABC COMPANY - Firmware Division')
team = Team.objects.create(organization=org, name='Build Automation')
project = Project.objects.create(team=team, name='SYSFW-TDA4VM', repo_url='https://github.com/example/sysfw')
print(f'Created: {project}')
"
```

### 5. Load pipeline configuration from JSON

```bash
python manage.py load_pipeline_config configs/pipeline_sysfw.json --project-id 1
```

### 6. Create simulated runs (for testing)

```bash
python manage.py simulate_run 1 --complete  # Complete run
python manage.py simulate_run 1             # Partial run with random completion
```

### 7. Create admin user

```bash
python manage.py createsuperuser
```

### 8. Start development server

```bash
python manage.py runserver 8001
```

## API Endpoints

### Pipelines
- `GET /api/pipelines/` - List all pipelines with full hierarchy
- `GET /api/pipelines/{id}/` - Get pipeline detail
- `GET /api/pipelines/{id}/trend/?n=10` - Get trend of last N runs

### Runs
- `GET /api/runs/` - List all runs
- `POST /api/runs/` - Create new run (payload: `{"pipeline": 1, "triggered_by": "Jenkins"}`)
- `GET /api/runs/{id}/summary/` - Get detailed run summary with all results
- `POST /api/runs/{id}/update_stage/` - Update stage/substage completion
  - Payload: `{"stage_id": 1, "completion_percent": 75, "status": "partial"}`
  - Or: `{"substage_id": 3, "completion_percent": 100, "status": "completed"}`

### Admin
- `http://127.0.0.1:8001/admin/` - Django admin interface

## Example API Usage

```bash
# Get pipeline with all stages/substages
curl http://127.0.0.1:8001/api/pipelines/1/

# Get run summary with results
curl http://127.0.0.1:8001/api/runs/2/summary/

# Get trend (last 5 runs)
curl 'http://127.0.0.1:8001/api/pipelines/1/trend/?n=5'

# Create new run
curl -X POST http://127.0.0.1:8001/api/runs/ \
  -H "Content-Type: application/json" \
  -d '{"pipeline": 1, "triggered_by": "Manual Test"}'

# Update substage completion
curl -X POST http://127.0.0.1:8001/api/runs/1/update_stage/ \
  -H "Content-Type: application/json" \
  -d '{"substage_id": 1, "completion_percent": 100, "status": "completed"}'
```

## Project Structure

```
tracker/
├── configs/
│   └── pipeline_sysfw.json       # Sample pipeline configuration
├── project/                       # Django project settings
│   ├── settings.py
│   └── urls.py
├── tracker/                       # Main app
│   ├── models.py                  # Domain models (9 models)
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # ViewSets with custom actions
│   ├── urls.py                    # API routing
│   ├── services.py                # Score calculation logic
│   ├── admin.py                   # Django admin registration
│   ├── signals.py                 # Auto-create results on Run creation
│   ├── apps.py                    # App config (signal registration)
│   └── management/commands/
│       ├── load_pipeline_config.py  # Load JSON → DB
│       └── simulate_run.py          # Create test runs
├── manage.py
├── requirements.txt
└── README.md
```

## Key Features Implemented

✅ **Organization → Team → Project → Pipeline hierarchy**  
✅ **JSON-driven pipeline configuration** (stages, substages, weights, DoD)  
✅ **Weighted score calculation** (normalized by stage weights)  
✅ **RESTful API** with DRF (pipelines, runs, trends)  
✅ **Signal-based auto-creation** of results for new runs  
✅ **Management commands** for config loading and testing  
✅ **Django admin** for quick browsing  
✅ **Trend analysis** endpoint for dashboard metrics

## Next Steps

- Add authentication/permissions (JWT or Django session auth)
- Build frontend dashboard (React/Vue) consuming the API
- Add more pipeline configs for different teams (webapp, mobile, etc.)
- Implement webhook endpoints for CI/CD integration (Jenkins, GitHub Actions)
- Add automated validation via the `auto_check_endpoint` field
- Deploy to production (Gunicorn + Nginx + PostgreSQL)
