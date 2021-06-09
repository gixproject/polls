#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

echo "Starting server"
python manage.py runserver_plus
