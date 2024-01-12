ARG DEP_IMAGE="dependencies-image"

FROM python:3.11-slim-bullseye as base-image
LABEL maintainer="Eldar Khabibulin"

# Configure environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    SOURCE_DATE_EPOCH=315532800 \
    CFLAGS=-g0 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    # poetry install is basically DDOSing PYPI if you have a lot of cores:
    # https://github.com/python-poetry/poetry/pull/3516
    POETRY_INSTALLER_MAX_WORKERS=2 \
    # make poetry install itself to this location
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR="$HOME/.cache/pypoetry" \
    POETRY_CONFIG_DIR="$HOME/.config/pypoetry" \
    # make poetry create the virtual environment in the `project's-root/.venv`
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.3.2 \
    POETRY_INSTALL_OPTS="--no-interaction --without dev --no-root" \
    # this is where our requirements + virtual environment will live
    APP_PATH="/pysetup" \
    APP_VENV_PATH="/pysetup/.venv" \
    # noninteractive installations in apt-get
    DEBIAN_FRONTEND=noninteractive

ENV PATH="${POETRY_HOME}/bin:${APP_VENV_PATH}/bin:${PATH}"

# Configure Debian snapshot archive 
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20220124 bullseye main" > /etc/apt/sources.list && \
    echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20220124 bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20220124 bullseye-updates main" >> /etc/apt/sources.list && \
    # Install build tools and dependencies
    apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

## Dependencies image with packages in venv created by poetry itself at `$APP_VENV_PATH`
FROM base-image as dependencies-image

ARG BUILD_ARG_PRIVATE_PACKAGES_USER
ARG BUILD_ARG_PRIVATE_PACKAGES_PASSWORD

RUN python -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install -U pip setuptools \
    && curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} POETRY_VERSION=${POETRY_VERSION} python3 - \
    && poetry config http-basic.private-packages $BUILD_ARG_PRIVATE_PACKAGES_USER $BUILD_ARG_PRIVATE_PACKAGES_PASSWORD \
    && rm -rf $POETRY_CACHE_DIR

WORKDIR $APP_PATH
COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && rm $POETRY_CONFIG_DIR/auth.toml


## Copy of dependencies image as it is usually built elswhere with `${DEP_IMAGE}` name
# See here: https://github.com/moby/moby/issues/34482#issuecomment-332298635
# why it is not possible to make `COPY --from=${DEP_IMAGE}` straightforward
FROM ${DEP_IMAGE} as dependencies-image-copy


FROM dependencies-image-copy as src-image

COPY . $APP_PATH


## Builder image that installs app to venv as .whl package
FROM src-image AS builder-image

# Install project without root package, then build and install from wheel.
# This is needed because Poetry doesn't support installing root package without
# editable mode: https://github.com/python-poetry/poetry/issues/1382
# Otherwise venv with source code would need to be copied to final image.
RUN poetry build \
    && $APP_VENV_PATH/bin/pip install --no-deps dist/*.whl


# Image for tests and linters
FROM src-image as test-app-image

RUN poetry install

ENTRYPOINT [ "poetry", "run" ]


FROM python:3.11-slim-bullseye as prod-app-image
LABEL maintainer="Eldar Khabibulin"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VENV_PATH="/pysetup/.venv"

COPY --from=builder-image $APP_VENV_PATH $APP_VENV_PATH

ENV PATH="${APP_VENV_PATH}/bin:${PATH}"

USER nonroot

EXPOSE 8000/tcp

STOPSIGNAL SIGINT

ENTRYPOINT ["core"]

CMD ["serve", "--bind", "0.0.0.0:8000"]