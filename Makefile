.PHONY: install test coverage coverage-report coverage-html

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

frontend-run: install-frontend
	uvicorn frontend.asgi:application --reload --port 8080

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

