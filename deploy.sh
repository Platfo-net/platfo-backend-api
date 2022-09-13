#!/bin/bash

docker compose -f docker-compose-prod.yaml down

# docker rmi botinow-backend-app:latest


# docker compose -f docker-compose-prod.yaml up -d