.PHONY: install test coverage coverage-report coverage-html

CI_COMMIT_SHA ?= $(shell git rev-parse HEAD)

install:
	poetry install

install-scraper:
	poetry install --with scraper

install-api:
	poetry install --with api

install-frontend:
	poetry install --with frontend

install-test:
	poetry install --with test

test: install-test
	poetry run pytest tests/

install-fmt:
	poetry install --with fmt

# EXECUTION COMMAND
scrape: install-scraper
	scraper

schema: install
	generate_schema

api-run: install-api
	python ./nfmer/api/v1/api.py

docker-api-build:
	docker build --target api -t "${CI_COMMIT_SHA}" .
	docker tag "${CI_COMMIT_SHA}" "nfmer-api:local"

docker-api-run:
	docker run -p 8000:8000 -v ./events.db:/home/nobody/events.db --rm nfmer-api:local

frontend-run: install-frontend
	cd nfmer/frontend && uvicorn frontend.asgi:application --reload --port 8080

docker-frontend-build:
	docker build --target frontend -t "${CI_COMMIT_SHA}" .
	docker tag "${CI_COMMIT_SHA}" "nfmer-frontend:local"

# LINTING
python-fmt: install-fmt
	poetry run black .
	poetry run isort .

python-check: install-fmt
	poetry run black . --check
	poetry run isort . --check
	poetry run flake8 --max-line-length 120 .
	poetry run mypy --show-error-codes .

# TESTS:
coverage: install-test
	poetry run coverage run -m pytest tests/

coverage-report: coverage
	poetry run coverage report

coverage-html: coverage
	poetry run coverage html

coverage-all: coverage coverage-report coverage-html

