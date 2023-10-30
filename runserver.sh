#!/bin/bash

export ENVIRONMENT="prod"
python ./app/pre_start.py

alembic upgrade head

python ./app/initial_data.py

gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$1
