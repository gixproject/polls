#!/bin/sh

python manage.py makemigrations --check --dry-run
pytest --disable-pytest-warnings
flake8 .
