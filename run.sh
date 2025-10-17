#!/usr/bin/with-contenv bashio

echo "Starting Shelly Scanner..."

# Get configuration
export ADMIN_PASSWORD=$(bashio::config 'admin_password')

# Start the Flask application
cd /app
python3 app.py
