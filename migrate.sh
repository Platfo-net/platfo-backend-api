#!/bin/bash

alembic upgrade head

python ./app/initial_data.py