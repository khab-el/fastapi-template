.DEFAULT_GOAL:=help

.EXPORT_ALL_VARIABLES:

ifndef VERBOSE
.SILENT:
endif

# set default shell
SHELL=/usr/bin/env bash -o pipefail -o errexit

TAG ?= $(shell cat TAG)
POETRY_HOME ?= ${HOME}/.local/share/pypoetry
POETRY_BINARY ?= ${POETRY_HOME}/venv/bin/poetry
POETRY_VERSION ?= 1.3.2

CODE = src tests

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: show-version
show-version:  ## Display version
	echo -n "${TAG}"

.PHONY: build
build: ## Build core package
	echo "[build] Build core package."
	${POETRY_BINARY} build

.PHONY: install
install:  ## Install core with poetry
	@build/install.sh

.PHONY: image
image:  ## Build core image
	@build/image.sh

.PHONY: local-db
local-db:  ## Run local db in docker
	@build/db.sh

.PHONY: start-service
start-service:  ## Run local service
	core serve --bind 0.0.0.0:8000

.PHONY: pre-commit-install
pre-commit-install:  ## Install pre-commit hook
	poetry run pre-commit install

.PHONY: unit-test
unit-test: ## Run core unit tests
	echo "[unit-test] Run core unit tests."
	${POETRY_BINARY} run pytest tests/unit

.PHONY: integration-test
integration-test: ## Run core integration tests
	echo "[unit-test] Run core integration tests."
	${POETRY_BINARY} run pytest tests/integration

.PHONY: coverage
coverage:  ## Run core tests coverage
	echo "[coverage] Run core tests coverage."
	${POETRY_BINARY} run pytest --cov=example --cov-fail-under=90 --cov-report=xml --cov-report=term-missing tests

.PHONY: test
test: unit-test integration-test  ## Run core tests

.PHONY: docs
docs: ## Build core documentation
	echo "[docs] Build core documentation."
	${POETRY_BINARY} run sphinx-build docs site

.PHONY: mypy
mypy:  ## Run core mypy checks
	echo "[mypy] Run core mypy checks."
	${POETRY_BINARY} run mypy --config-file pyproject.toml $(CODE)

.PHONY: migrate-create
migrate-create: ## Create a new revision file
	poetry run alembic revision --autogenerate

.PHONY: migrate-up
migrate-up: ## Upgrade to a later version
	poetry run alembic upgrade head

.PHONY: migrate-down
migrate-down: ## Revert to a previous version
	poetry run alembic downgrade $(revision)

#* Formatters
.PHONY: format
format:  ## Format code
	echo "Run format code."
	echo "[pyupgrade] [autoflake] Run code upgrade."
	${POETRY_BINARY} run pyupgrade --exit-zero-even-if-changed --py311-plus **/*.py
	${POETRY_BINARY} run autoflake $(CODE)
	echo "[add-trailing-comma] [isort] [black] Run code style format."
	${POETRY_BINARY} run add-trailing-comma --exit-zero-even-if-changed **/*.py
	${POETRY_BINARY} run isort $(CODE)
	${POETRY_BINARY} run black $(CODE)

#* Validate pyproject.toml
.PHONY: check-poetry
check-poetry:
	echo "[poetry] Run pyproject.toml check."
	${POETRY_BINARY} check

#* Check code style
.PHONY: check-codestyle
check-codestyle:
	echo "[isort] [black] Run code style check."
	${POETRY_BINARY} run isort --diff --check-only $(CODE)
	${POETRY_BINARY} run black --diff --check $(CODE)

#* Check static linters
.PHONY: static-lint
static-lint:
	echo "[flake8] [mypy] [pylint] Run static lint check."
	${POETRY_BINARY} run flake8 $(CODE)
	${POETRY_BINARY} run mypy --config-file pyproject.toml $(CODE)
	${POETRY_BINARY} run pylint --errors-only $(CODE)

#* Check security issues
.PHONY: check-security
check-security:
	${POETRY_BINARY} run bandit -ll --recursive src

.PHONY: lint
lint: check-poetry check-codestyle static-lint check-security  ## Check linting code
