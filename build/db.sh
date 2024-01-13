#!/usr/bin/env bash

if [ -n "$DEBUG" ]; then
	set -x
fi

set -o errexit
set -o nounset
set -o pipefail

if command -v docker &> /dev/null; then
    docker run --name template \
    -d \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -e POSTGRES_DB=core \
    -p 7433:5432 \
    postgres:15
else
    echo "[image] Neither docker nor podman container engine found."
    exit 1
fi