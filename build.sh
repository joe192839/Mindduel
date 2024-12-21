#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip
pip install gunicorn
pip install -r requirements.txt

mkdir -p static/css/dist
mkdir -p staticfiles
cd theme/static_src
npm install
npm run build

cd ../..
# Collect static files
python manage.py collectstatic --no-input
python manage.py migrate
