.PHONY: install test coverage coverage-report coverage-html

install-test:
	poetry install --with test

test: install-test
	poetry run pytest tests/

coverage: install-test
	poetry run coverage run -m pytest tests/

coverage-report: coverage
	poetry run coverage report

coverage-html: coverage
	poetry run coverage html

# Run all coverage commands in sequence
coverage-all: coverage coverage-report coverage-html

