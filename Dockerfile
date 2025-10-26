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
        py3-flask \
        py3-requests \
    || (pip3 install --no-cache-dir --break-system-packages \
        flask==3.0.0 \
        requests==2.31.0)

# Copy root filesystem
COPY rootfs /

# Make service scripts executable
RUN chmod a+x /etc/services.d/shelly-scanner/run \
    && chmod a+x /etc/services.d/shelly-scanner/finish

# Set working directory
WORKDIR /app

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="filmgarage" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="filmgarage" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/filmgarage/ha-addon-shelly-scanner" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
