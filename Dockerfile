ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-flask

# Copy application files
COPY run.sh /
COPY app /app

RUN chmod a+x /run.sh

WORKDIR /app

CMD [ "/run.sh" ]
