#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start the Shelly Scanner service
# ==============================================================================

bashio::log.info "Starting Shelly Scanner..."

# Get configuration
export ADMIN_PASSWORD=$(bashio::config 'admin_password')
export NETWORK_RANGE=$(bashio::config 'network_range')

# Log configuration (without showing password)
if bashio::var.has_value "${ADMIN_PASSWORD}"; then
    bashio::log.info "Admin password configured"
else
    bashio::log.warning "No admin password set - limited functionality"
fi

if bashio::var.has_value "${NETWORK_RANGE}"; then
    bashio::log.info "Custom network range configured: ${NETWORK_RANGE}"
else
    bashio::log.info "Using auto-detected network range (/24)"
fi

# Set port for ingress
export INGRESS_PORT=8099
export PORT=8099

# Start the Flask application
bashio::log.info "Starting Flask application..."
cd /app
exec python3 -u app.py
