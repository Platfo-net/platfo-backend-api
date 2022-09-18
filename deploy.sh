#!/bin/bash
export DOCKER_BUILDKIT=1
export TAG="$(git rev-parse --short HEAD)"
echo "Current image tag is: ${TAG}"

docker-compose -f docker-compose-stage.yaml down --remove-orphans

docker rmi botinow-backend-app:latest

if  [ "$1" = "--build" ] ; then
    echo "Building the images"
    docker-compose -f docker-compose-stage.yaml build
else
    echo "Pulls the tagged images without building from local registry."
fi
docker-compose -f docker-compose-stage.yaml pull

COMPOSE_HTTP_TIMEOUT=300 docker-compose -f docker-compose-stage.yaml up -d --no-build
