#!/bin/bash
set -e

#Wait for db to start
python ./app/tests_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./app/initial_test_data.py

# Run tests
pytest  --traceconfig --print tests
# --cov=app --cov-report=term-missing tests