#!/bin/bash


alembic upgrade head

python ./app/initial_data.py
#Start app

gunicorn app.main:app --workers 6 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000