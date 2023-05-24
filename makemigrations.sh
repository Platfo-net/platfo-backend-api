#!/bin/bash

docker compose run api sh -c "alembic revision --autogenerate -m $1"
