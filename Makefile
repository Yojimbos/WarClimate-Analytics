PYTHON ?= python
COMPOSE ?= docker compose

run:
	$(COMPOSE) up --build

test:
	cd backend && $(PYTHON) -m pytest

lint:
	cd backend && $(PYTHON) -m ruff check app tests
	cd backend && $(PYTHON) -m ruff format --check app tests

seed:
	cd backend && $(PYTHON) -m app.cli seed --with-sample-data

ingest:
	cd backend && $(PYTHON) -m app.cli ingest --days 30 --location kyiv

build:
	$(COMPOSE) build

