# Makefile for csplanet (Django + Docker)

# Path to your local compose file and service name
COMPOSE = docker compose -f docker-compose.local.yml
SERVICE = django

.PHONY: reset down build up restart migrate makemigrations createsuperuser runserver shell collectstatic logs

#―――――――――――――――――――――――――――――――
# Environment reset: stop containers, remove volumes & orphans
reset:
	@$(COMPOSE) down -v --remove-orphans

# Stop services without pruning volumes
down:
	@$(COMPOSE) down

# Build images
build:
	@$(COMPOSE) build

# Bring services up in detached mode
up:
	@$(COMPOSE) up -d

# Full restart (reset + up)
restart: reset up

#―――――――――――――――――――――――――――――――
# Django management commands inside container
migrate:
	@$(COMPOSE) exec $(SERVICE) python manage.py migrate

makemigrations:
	@$(COMPOSE) exec $(SERVICE) python manage.py makemigrations

createsuperuser:
	@$(COMPOSE) exec $(SERVICE) python manage.py createsuperuser

# Run development server
runserver:
	@$(COMPOSE) exec $(SERVICE) python manage.py runserver 0.0.0.0:8000

# Bash shell inside container
shell:
	@$(COMPOSE) exec $(SERVICE) bash

# Collect static files
collectstatic:
	@$(COMPOSE) exec $(SERVICE) python manage.py collectstatic --noinput

# Stream logs
logs:
	@$(COMPOSE) logs -f
