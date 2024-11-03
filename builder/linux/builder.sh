#!/bin/bash

# Create a temporary directory for the Wine prefix
TMPDIR=$(pwd)/.python

# Create a Wine prefix in the temporary directory
mkdir .python

# Change to the temporary directory
cd $TMPDIR
cp -t . /game-code/*

uv run pyinstaller --onefile --clean main.py

mv dist/main ../../output/linux_game

# Go back to starting folder
cd ..

# Cleanup
sleep 5
rm -rf .python