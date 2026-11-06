# Health Information System API

A modular, multi-tenant REST API for healthcare operations, built for clinics, community health programs, and service organizations. The platform supports authentication, organizations, client records, health programs, care workflows, service delivery, reporting, integrations, and subscriptions.

**Production URL:** https://health-information-system-6qbudrf53q-ue.a.run.app

## Current Capabilities

- JWT authentication and role-based authorization
- Organization management, memberships, and invitations
- Client registration, search, profiles, records, and program enrollment
- Program lifecycle management
- Appointments, follow-ups, referrals, and care workflows
- Assessment templates, service delivery, and corrections
- Dashboard and program reporting with CSV exports
- Client import preview, credentials, webhooks, and delivery tracking
- Billing plans, subscriptions, entitlements, invoices, and usage
- Liveness and database-readiness health checks

## Architecture

The application follows a layered Flask architecture:

- `app/routes/` — HTTP endpoints and request handling
- `app/services/` — business and workflow logic
- `app/models/` — SQLAlchemy persistence models
- `app/schemas/` — request validation and serialization
- `migrations/` — Flask-Migrate/Alembic database migrations
- `tests/` — automated API and business-rule coverage

## Technology Stack

- Python and Flask
- Flask-SQLAlchemy and Flask-Migrate
- Flask-JWT-Extended
- Marshmallow
- bcrypt
- pytest
- PostgreSQL in production; SQLite for local development
- Gunicorn on deployed environments

## Local Development

### Prerequisites

- Python 3.11 or 3.12
- Git

### Setup

```bash
git clone https://github.com/Agostinejohn/health-information-system.git
cd health-information-system

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
flask --app run db upgrade
python run.py
```

The API starts on `http://localhost:5000`.

### Example Environment Variables

```dotenv
FLASK_ENV=development
SECRET_KEY=replace-with-a-long-random-value
JWT_SECRET_KEY=replace-with-another-long-random-value
DATABASE_URL=sqlite:///health.db
```

Production environments must use secure secrets and a PostgreSQL database. Never commit real credentials.

## API Overview

### Health and Authentication

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/live` | Liveness check |
| GET | `/health/ready` | Database readiness check |
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate and receive a JWT |

### Organizations, Programs, and Clients

| Method | Endpoint | Description |
|---|---|---|
| POST/GET | `/organizations` | Create or list organizations |
| GET/PATCH | `/organizations/<organization_id>` | Organization details and updates |
| POST | `/organizations/<organization_id>/invitations` | Invite an organization member |
| POST | `/organizations/invitations/accept` | Accept an invitation |
| POST/GET | `/programs` | Create or list programs |
| GET/PATCH | `/programs/<program_id>` | Program details and lifecycle updates |
| POST | `/programs/<program_id>/enrollments` | Enroll a client |
| POST/GET | `/clients` | Register or list clients |
| GET/PATCH | `/clients/<client_id>` | Client details and updates |

### Care and Service Delivery

| Method | Endpoint | Description |
|---|---|---|
| POST/GET | `/appointments` | Manage appointments |
| PATCH | `/appointments/<appointment_id>` | Update an appointment |
| POST/GET | `/follow-ups` | Manage follow-ups |
| POST/GET | `/referrals` | Manage referrals |
| POST/GET | `/assessment-templates` | Manage assessment templates |
| POST/GET | `/service-deliveries` | Record and list service deliveries |
| POST | `/service-deliveries/<delivery_id>/corrections` | Submit a delivery correction |

### Reporting and Integrations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/reports/dashboard` | Dashboard metrics |
| GET | `/reports/programs` | Program reporting |
| POST/GET | `/reports/exports` | Create and list report exports |
| GET | `/reports/exports/<export_id>/csv` | Download a CSV export |
| POST | `/integrations/imports/clients/preview` | Preview a client import |
| POST | `/integrations/imports/clients/commit` | Commit an idempotent client import |
| POST/GET | `/integrations/credentials` | Manage integration credentials |
| POST/GET | `/integrations/webhooks` | Create and list webhooks |
| POST | `/integrations/webhooks/<endpoint_id>/deliveries` | Trigger a webhook delivery |

### Billing

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/billing/plans` | List or create billing plans |
| GET | `/billing/subscription` | View the active subscription |
| POST | `/billing/subscription/change-plan` | Change subscription plan |
| POST | `/billing/subscription/lifecycle` | Update subscription lifecycle state |
| GET | `/billing/entitlements` | Read plan entitlements |
| GET/POST | `/billing/invoices` | List or create invoices |
| POST | `/billing/invoices/<invoice_id>/status` | Update invoice status |
| GET | `/billing/usage` | Read usage records |

Protected endpoints require an authorization header:

```http
Authorization: Bearer <access-token>
```

## Authentication Example

```bash
curl -X POST http://localhost:5000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.org","password":"a-secure-password","role":"admin"}'

curl -X POST http://localhost:5000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.org","password":"a-secure-password"}'
```

Copy the returned `access_token` and send it with protected requests.

## Roles

- `admin` — organization and system administration
- `doctor` / `health_worker` — client and care-work operations
- Additional roles are validated by organization-aware authorization policies

## Tests

```bash
pytest -q
```

The full suite currently contains 68 passing tests.

## Database Migrations

```bash
flask --app run db upgrade
flask --app run db downgrade
flask --app run db history
```

## Production Deployment

Iteration 10 deployment is hosted on Google Cloud Run:

- Production URL: https://health-information-system-6qbudrf53q-ue.a.run.app
- Platform: Google Cloud Run, `us-east1`
- Container registry: Google Artifact Registry
- Database: Cloud SQL PostgreSQL 16
- Secrets: Google Secret Manager
- Runtime: Gunicorn inside the Docker container

Deployment endpoints:

| Endpoint | Purpose |
|---|---|
| `/` | API landing response |
| `/health/live` | Container liveness check |
| `/health/ready` | Database readiness check |

The landing response only confirms that the API is running. The application features are available under routes documented above, including authentication, organizations, clients, programs, care workflows, service delivery, reporting, integrations, and billing.

Database migrations are applied through a Cloud Run migration job. Google Cloud Run is the current and verified production deployment.

See `Dockerfile`, `Procfile`, and `config.py` for container and runtime configuration.

## Deployment Status

- Production API: Google Cloud Run
- Production database: Cloud SQL PostgreSQL
- Production secrets: Secret Manager
- Container deployments: Artifact Registry and manual Cloud Build
- GitHub Actions deployment automation: planned

## Roadmap

- Production custom domain
- Monitoring dashboards and alert policies
- Cloud SQL backup and restore verification
- Automated GitHub Actions deployment
- OpenAPI/Swagger API documentation
- Web frontend and customer-facing interface

## Security

- Keep JWT and application secrets outside source control
- Use HTTPS for all production API traffic
- Rotate integration credentials and revoke unused credentials
- Apply database backups and least-privilege credentials before production rollout
- Review organization membership and role checks before exposing admin operations

## Repository

- GitHub: https://github.com/Agostinejohn/health-information-system
- Live API: https://health-information-system-6qbudrf53q-ue.a.run.app

## License

License information has not yet been added. Do not distribute the project publicly as open source until a license is selected.
