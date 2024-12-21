#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install gunicorn
pip install -r requirements.txt

# Ensure directories exist
mkdir -p static/css/dist
mkdir -p staticfiles
mkdir -p theme/static_src/node_modules

# Install and build Tailwind CSS
cd theme/static_src
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found in theme/static_src"
    exit 1
fi

# Install Node.js dependencies
npm install

# Build Tailwind CSS
npm run build

# Return to project root
cd ../..

# Run Django commands
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py migrate --noinput