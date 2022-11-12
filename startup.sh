#!/bin/bash

export ENVIRONMENT="dev"

python ./app/pre_start.py

alembic upgrade head

python ./app/initial_data.py
#Start app

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload