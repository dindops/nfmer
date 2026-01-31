FROM python:3.13-slim-bookworm AS build-stage

WORKDIR /home/nobody

ARG GID=1000
ARG UID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONASYNCIODEBUG=0 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PATH="/home/nobody/.venv/bin:$PATH" \
    PYTHONPATH="$PYTHONPATH:/home/nobody/nfmer"

RUN usermod -d /home/nobody nobody \
    && chown -R "${UID}":"${GID}" /home/nobody

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY --chown="${uid}":"${gid}" pyproject.toml poetry.lock ./

RUN poetry install --only main,api --no-root --no-ansi

FROM python:3.13-slim-bookworm AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONASYNCIODEBUG=0 \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PATH="/home/nobody/.venv/bin:$PATH" \
    PYTHONPATH="$PYTHONPATH:/home/nobody/nfmer"

WORKDIR /home/nobody
RUN usermod -d /home/nobody nobody \
    && chown -R "${UID}":"${GID}" /home/nobody

RUN apt-get update && apt-get dist-upgrade -y && apt-get install net-tools &&  apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build-stage --chown="${uid}":"${gid}" /home/nobody/.venv /home/nobody/.venv
COPY --chown="${uid}":"${gid}" nfmer nfmer

USER nobody

CMD ["python", "-m", "uvicorn", "nfmer.api.v1.api:api", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
