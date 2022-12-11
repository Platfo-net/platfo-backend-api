#!/bin/bash


PREVIOUS_ENVIRONMENT=$ENVIRONMENT
export ENVIRONMENT="test"

echo Environment switch from $PREVIOUS_ENVIRONMENT to $ENVIRONMENT
#Creating test DB
python ./app/create_test_db.py

#Wait for db to start
python ./app/tests_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./app/initial_test_data.py

# Run tests
pytest --disable-warnings tests
TEST_RESULT=$?
# --cov=app --cov-report=term-missing tests

#Purge test DB
python ./app/purge_test_db.py

export ENVIRONMENT=$PREVIOUS_ENVIRONMENT

echo Environment switch from test to $ENVIRONMENT

flake8 tests/

LINT_EXIT_CODE=$?

if [ $TEST_RESULT == 0 ] && [ $LINT_EXIT_CODE == 0 ]; 
then
    echo Test Done Successfully
    exit 0
else
    echo Test Done With Error
    exit 1
fi