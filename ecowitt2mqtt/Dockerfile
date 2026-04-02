ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-alpine:3.19
FROM $BUILD_FROM

ARG TARGETPLATFORM

ENV CRYPTOGRAPHY_VERSION=41.0.7 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
	POETRY_VERSION=2.1.2 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

RUN apk add --no-cache \
	bash \
	build-base \
	libffi-dev \
    python3 \
    py3-pip \
    python3-dev

COPY / /app/

RUN pip3 install --break-system-packages --no-cache-dir --upgrade pip \
    && pip3 install --break-system-packages poetry==${POETRY_VERSION} "poetry-plugin-export" \
    && poetry export --without-hashes -f requirements.txt --only main | pip3 install --break-system-packages -r /dev/stdin \
    && pip3 install --break-system-packages /app

RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]