#!/bin/bash

alias butler='~/.config/itch/apps/butler/butler'

mkdir temp_game
mkdir output
mkdir output/windows
mkdir output/linux

cp -t temp_game/. ../*

# Build the Docker image
docker build -t game-builder .

# Run the Docker container and wait until it finishes
docker run --rm -v $(pwd):/game -v $(pwd)/temp_game:/game-code game-builder

# Remove the Docker image
docker image rm game-builder

rm -rf temp_game

butler push output/windows lunamidori/midori-endless-auto-fighter:windows
butler push output/linux lunamidori/midori-endless-auto-fighter:linux