# Email Audit Service

A Django-based email auditing service for tracking and analyzing email communications.

## Features

- Django 5.2.3 with modern Python 3.13
- PostgreSQL database support
- **Celery with Redis** for asynchronous task processing
- Docker containerization with Gunicorn
- Environment-based configuration
- Production-ready setup

## Project Structure

```
email-audit-service/
├── audit/                  # Django app for audit functionality
│   ├── tasks.py           # Celery tasks for async processing
│   └── management/commands/ # Management commands
├── email_audit/           # Main Django project
│   └── celery.py          # Celery configuration
├── docker-compose.yml     # Production Docker setup (with Redis & Celery)
├── docker-compose.dev.yml # Development Docker setup
├── Dockerfile            # Docker image configuration
├── docker-manage.sh      # Docker management script
└── requirements managed by uv
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email-audit-service
   ```

2. **Start development environment**
   ```bash
   ./docker-manage.sh dev
   ```

3. **Run migrations** (in another terminal)
   ```bash
   ./docker-manage.sh migrate
   ```

4. **Create a superuser**
   ```bash
   ./docker-manage.sh createsuperuser
   ```

5. **Access the application**
   - Django app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Production Setup

1. **Build and start services**
   ```bash
   ./docker-manage.sh build
   ./docker-manage.sh up
   ```

2. **Run initial setup**
   ```bash
   ./docker-manage.sh migrate
   ./docker-manage.sh collectstatic
   ./docker-manage.sh createsuperuser
   ```

3. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Docker Management

The `docker-manage.sh` script provides convenient commands for managing the Docker environment:

### Available Commands

| Command | Description |
|---------|-------------|
| `./docker-manage.sh build` | Build Docker images |
| `./docker-manage.sh up` | Start services in production mode |
| `./docker-manage.sh dev` | Start services in development mode |
| `./docker-manage.sh down` | Stop all services |
| `./docker-manage.sh logs` | Show service logs |
| `./docker-manage.sh migrate` | Run Django migrations |
| `./docker-manage.sh collectstatic` | Collect static files |
| `./docker-manage.sh shell` | Open Django shell |
| `./docker-manage.sh createsuperuser` | Create Django superuser |
| `./docker-manage.sh test` | Run tests |
| `./docker-manage.sh clean` | Clean up Docker resources |

### Development Workflow

```bash
# Start development environment
./docker-manage.sh dev

# Run migrations when models change
./docker-manage.sh migrate

# Run tests
./docker-manage.sh test

# View logs
./docker-manage.sh logs

# Stop services
./docker-manage.sh down
```

### Production Deployment

```bash
# Build images
./docker-manage.sh build

# Start production services
./docker-manage.sh up

# Run initial setup
./docker-manage.sh migrate
./docker-manage.sh collectstatic

# Monitor logs
./docker-manage.sh logs
```

## Services

### Docker Compose Services

- **web**: Django application with Gunicorn WSGI server
- **db**: PostgreSQL 15 database
- **redis**: Redis server for Celery task queue
- **celery**: Celery worker for asynchronous task processing

### Port Mapping

- **Development**:
  - Django: http://localhost:8000
  - PostgreSQL: localhost:5432
  - Redis: localhost:6379

- **Production**:
  - Django: http://localhost:8000
  - PostgreSQL: localhost:5432
  - Redis: localhost:6379

## Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

### Key Environment Variables

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database settings
DATABASE_URL=postgres://postgres:postgres@db:5432/email_audit
POSTGRES_DB=email_audit
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Celery settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Development

### Local Development (without Docker)

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Run migrations**
   ```bash
   uv run python manage.py migrate
   ```

3. **Start development server**
   ```bash
   uv run python manage.py runserver
   ```

### Running Tests

```bash
# With Docker
./docker-manage.sh test

# Local development
uv run python manage.py test
```

### Database Management

```bash
# Create migrations
./docker-manage.sh shell
uv run python manage.py makemigrations

# Apply migrations
./docker-manage.sh migrate

# Access Django shell
./docker-manage.sh shell
```

### Celery Task Management

```bash
# View Celery worker logs
docker-compose logs celery

# Monitor Celery worker in real-time
docker-compose logs -f celery
```

### Available Celery Tasks

- `process_email_audit(email_data)` - Process individual email audits
- `batch_process_emails(email_ids)` - Process multiple emails in batch

### API Endpoints

- `POST /api/audit/queue-email-audit/` - Queue an email for audit
- `POST /api/audit/batch-audit/` - Queue batch email processing
- `GET /api/audit/health/` - Health check endpoint

## Production Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use strong database passwords
- Set up SSL/TLS certificates
- Configure proper logging
- Set up monitoring and backups

## Technology Stack

- **Backend**: Django 5.2.3, Python 3.13
- **Database**: PostgreSQL 15
- **Task Queue**: Celery 5.3+ with Redis 7
- **WSGI Server**: Gunicorn
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose

