#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies from your requirements.txt
pip install -r requirements.txt

# Run Django's 'collectstatic' to gather all CSS/JS/images
python manage.py collectstatic --no-input

# Run Django's database migrations
python manage.py migrate