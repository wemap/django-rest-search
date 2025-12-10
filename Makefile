export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH = $(PWD)

all:
	@echo "Usage: make test"
	@exit 1

lint:
	ruff check --diff
	ruff format --diff

test:
	coverage erase
	coverage run `which django-admin` test -v 1
	coverage report
	coverage xml
