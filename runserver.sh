#!/bin/bash


alembic upgrade head

python ./app/initial_data.py
#Start app


gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$1
