#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Shelly Scanner..."

# Get configuration
export ADMIN_PASSWORD=$(bashio::config 'admin_password')

if bashio::var.has_value "${ADMIN_PASSWORD}"; then
    bashio::log.info "Admin password configured"
else
    bashio::log.warning "No admin password set - limited functionality"
fi

# Check if we're running in ingress mode
if bashio::config.true 'ingress'; then
    bashio::log.info "Running in ingress mode"
else
    bashio::log.info "Running in standalone mode"
fi

# Start the Flask application
bashio::log.info "Starting Flask application on port 8099..."
cd /app

# Run with explicit host and port
python3 -u app.py 2>&1 | while read -r line; do
    bashio::log.info "$line"
done
