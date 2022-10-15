#!/bin/bash


docker compose -f docker-compose-test.yaml down 
docker volume rm botinow_postgres-data-test
docker volume rm botinow_redis-data-test

docker compose -f docker-compose-test.yaml up 
