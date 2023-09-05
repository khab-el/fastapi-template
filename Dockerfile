FROM python:3.11-slim-bullseye as builder
LABEL maintainer="Eldar Khabibulin"

# Configure environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    SOURCE_DATE_EPOCH=315532800 \
    CFLAGS=-g0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.3.2 \
    POETRY_INSTALL_OPTS="--no-interaction --without dev --no-root" \
    PYSETUP_PATH="/pysetup" \
    VENV_PATH="/pysetup/.venv"

ENV PATH="${POETRY_HOME}/bin:${VENV_PATH}/bin:${PATH}"

# Configure Debian snapshot archive
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20220124 bullseye main" > /etc/apt/sources.list && \
    echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20220124 bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20220124 bullseye-updates main" >> /etc/apt/sources.list

# Install build tools and dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl build-essential

# Install project without root package, then build and install from wheel.
# This is needed because Poetry doesn't support installing root package without
# editable mode: https://github.com/python-poetry/poetry/issues/1382
# Otherwise venv with source code would need to be copied to final image.
COPY . $PYSETUP_PATH
WORKDIR $PYSETUP_PATH
RUN make install && \
    poetry build && \
    $VENV_PATH/bin/pip install --no-deps dist/*.whl



FROM python:3.11-slim-bullseye as final
LABEL maintainer="Eldar Khabibulin"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH="/pysetup/.venv"

COPY --from=builder $VENV_PATH $VENV_PATH

ENV PATH="${VENV_PATH}/bin:${PATH}"

USER nonroot

EXPOSE 8000/tcp

STOPSIGNAL SIGINT

ENTRYPOINT ["core"]

CMD ["serve", "--bind", "0.0.0.0:8000"]