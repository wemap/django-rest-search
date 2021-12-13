export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH = $(PWD)

all:
	@echo "Usage: make test"
	@exit 1

lint:
	flake8 src tests
	isort --check-only --diff src tests
	black --check --diff src tests

test:
	coverage erase
	coverage run `which django-admin` test
	coverage report
	coverage xml
