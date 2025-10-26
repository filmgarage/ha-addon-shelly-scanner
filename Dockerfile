# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
    && pip3 install --no-cache-dir --break-system-packages \
        flask==3.0.0 \
        requests==2.31.0

# Copy root filesystem
COPY rootfs /

# Make service scripts executable
RUN chmod +x /etc/services.d/shelly-scanner/run && \
    chmod +x /etc/services.d/shelly-scanner/finish

# Set working directory
WORKDIR /app
