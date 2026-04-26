# Health Information System API

# Render API Link: https://health-information-system-ss87.onrender.com

A production-grade REST API for managing health programs and client enrollments. Built with Flask, SQLAlchemy, JWT authentication, and full test coverage.

## Tech Stack
- **Python / Flask** — web framework
- **SQLAlchemy + Flask-Migrate** — ORM and database migrations
- **Flask-JWT-Extended** — JWT authentication
- **Marshmallow** — input validation
- **bcrypt** — password hashing
- **pytest** — testing (98% coverage)
- **gunicorn** — production WSGI server

## Project Structure
```
app/
  models/       — database models (User, Client, Program)
  routes/       — API endpoints (auth, clients, programs)
  schemas/      — request validation
  services/     — business logic
tests/          — full test suite
migrations/     — database migration history
```

## Local Setup

```bash
git clone https://github.com/Agostinejohn/Health_Information_system.git
cd Health_Information_system

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # edit values inside

flask --app run db upgrade      # apply migrations

python run.py                   # starts on http://localhost:5000
```

## API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register a user |
| POST | `/auth/login` | Public | Login and get JWT token |

### Programs (Admin only)
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/programs` | Admin | Create a health program |
| GET | `/programs` | Any user | List all programs |

### Clients
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/clients` | Any user | Register a client |
| GET | `/clients?name=John` | Any user | Search clients by name |
| GET | `/clients/<id>` | Any user | View client profile |
| POST | `/clients/<id>/enroll` | Any user | Enroll client in programs |

## Example Usage

**1. Register an admin**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinic.com", "password": "secure123", "role": "admin"}'
```

**2. Login and get token**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinic.com", "password": "secure123"}'
```

**3. Create a program (use token from step 2)**
```bash
curl -X POST http://localhost:5000/programs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "TB"}'
```

**4. Register a client**
```bash
curl -X POST http://localhost:5000/clients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Wanjiku", "age": 32}'
```

**5. Enroll client in program**
```bash
curl -X POST http://localhost:5000/clients/<client_id>/enroll \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"program_ids": ["<program_id>"]}'
```

## Running Tests

```bash
pytest tests/ -v --cov=app
```

## Deployment (Render.com)

1. Push this repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set environment variables in the Render dashboard:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_URL` (from Render PostgreSQL instance)
   - `FLASK_ENV=production`
5. Set **Build Command**: `pip install -r requirements.txt && flask --app run db upgrade`
6. Set **Start Command**: `gunicorn run:app`
7. Deploy

## Roles
- `admin` — can create programs, access everything
- `doctor` — can register clients, enroll, search, view profiles
