.PHONY: build up down logs shell migrate collectstatic

build:
\tdocker-compose build

up:
\tdocker-compose up -d

down:
\tdocker-compose down

logs:
\tdocker-compose logs -f

shell:
\tdocker-compose exec web /bin/bash

migrate:
\tdocker-compose exec web python manage.py migrate

collectstatic:
\tdocker-compose exec web python manage.py collectstatic --noinput
