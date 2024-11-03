#!/bin/bash
mkdir temp_game

cp -t temp_game/. ../*

# Build the Docker image
docker build -t game-builder .

# Run the Docker container and wait until it finishes
docker run --rm -v $(pwd):/game -v $(pwd)/temp_game:/game-code game-builder

# Remove the Docker image
docker image rm game-builder