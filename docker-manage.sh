#!/bin/bash

# Email Audit Service Docker Management Script

case "$1" in
    "build")
        echo "Building Docker images..."
        docker-compose build
        ;;
    "up")
        echo "Starting services in production mode..."
        docker-compose up -d
        ;;
    "dev")
        echo "Starting services in development mode..."
        docker-compose -f docker-compose.dev.yml up
        ;;
    "down")
        echo "Stopping all services..."
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        ;;
    "logs")
        echo "Showing logs..."
        docker-compose logs -f
        ;;
    "migrate")
        echo "Running Django migrations..."
        docker-compose exec web uv run python manage.py migrate
        ;;
    "collectstatic")
        echo "Collecting static files..."
        docker-compose exec web uv run python manage.py collectstatic --noinput
        ;;
    "shell")
        echo "Opening Django shell..."
        docker-compose exec web uv run python manage.py shell
        ;;
    "createsuperuser")
        echo "Creating Django superuser..."
        docker-compose exec web uv run python manage.py createsuperuser
        ;;
    "test")
        echo "Running tests..."
        docker-compose exec web uv run python manage.py test
        ;;
    "clean")
        echo "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        ;;
    *)
        echo "Email Audit Service Docker Management"
        echo ""
        echo "Usage: $0 {build|up|dev|down|logs|migrate|collectstatic|shell|createsuperuser|test|clean}"
        echo ""
        echo "Commands:"
        echo "  build          - Build Docker images"
        echo "  up             - Start services in production mode"
        echo "  dev            - Start services in development mode"
        echo "  down           - Stop all services"
        echo "  logs           - Show service logs"
        echo "  migrate        - Run Django migrations"
        echo "  collectstatic  - Collect static files"
        echo "  shell          - Open Django shell"
        echo "  createsuperuser - Create Django superuser"
        echo "  test           - Run tests"
        echo "  clean          - Clean up Docker resources"
        ;;
esac
