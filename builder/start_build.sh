#!/bin/bash

# Build the Docker image
docker build -t my-image .

# Run the Docker container and wait until it finishes
docker run --rm -v $(pwd):/game my-image

# Remove the Docker image
docker image rm my-image