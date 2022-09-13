#!/bin/bash

docker compose -f docker-compose-stage.yaml down

docker rmi botinow-backend-app:latest


docker compose -f docker-compose-stage.yaml up -d