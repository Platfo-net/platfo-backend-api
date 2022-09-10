#!/bin/bash

docker compose down

docker rmi botinow-backend-app:latest

docker compose up -d