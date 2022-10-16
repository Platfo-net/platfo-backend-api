#!/bin/bash


alembic upgrade head

python ./app/initial_data.py
#Start app
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload