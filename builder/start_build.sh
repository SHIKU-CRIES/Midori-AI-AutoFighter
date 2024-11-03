#!/bin/bash

# Build the Docker image
docker build -t game-builder .

# Run the Docker container and wait until it finishes
docker run --rm -v $(pwd):/game game-builder

# Remove the Docker image
docker image rm game-builder