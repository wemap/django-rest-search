export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH = $(PWD)

all:
	@echo "Usage: make test"
	@exit 1

test:
	flake8 rest_search tests
	isort -c -df -rc rest_search tests
	coverage erase
	coverage run `which django-admin` test
	coverage report
