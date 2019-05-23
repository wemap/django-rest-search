export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH = $(PWD)

all:
	@echo "Usage: make test"
	@exit 1

lint:
	flake8 rest_search tests
	isort -c -df -rc rest_search tests
	black --check --diff rest_search tests

test:
	coverage erase
	coverage run `which django-admin` test
	coverage report
