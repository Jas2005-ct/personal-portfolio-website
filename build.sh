#!/usr/bin/env bash
# exit on error
set -o errexit

pip install poetry
poetry config virtualenvs.create false --local
poetry install

# Build Tailwind CSS
cd theme/static_src && npm ci && npm run build && cd ../..

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser_if_none_exists
