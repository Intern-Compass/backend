#!/usr/bin/env bash

set -e
set -x

# Run migrations
alembic upgrade head

# TODO: create initial db seed
