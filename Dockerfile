ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip && \
    pip3 install --no-cache-dir --break-system-packages \
    flask==3.0.0 \
    requests==2.31.0 \
    websocket-client==1.6.4

# Copy application files
COPY app /app

# Copy startup script
COPY run.sh /
RUN chmod +x /run.sh

# Set working directory
WORKDIR /app

# Start script
CMD ["/run.sh"]
