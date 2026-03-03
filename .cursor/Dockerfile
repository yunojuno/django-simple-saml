FROM ghcr.io/cursor-images/python-3.12:latest

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        xmlsec1 \
        libxmlsec1-dev \
        libxmlsec1-openssl \
        libxml2-dev \
        pkg-config \
        python3-dev \
        python3.12-venv \
    && rm -rf /var/lib/apt/lists/*
