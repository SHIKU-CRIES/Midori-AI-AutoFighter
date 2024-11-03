#!/bin/bash

# Create a temporary directory for the Wine prefix
TMPDIR=$(pwd)/.python

# Create a Wine prefix in the temporary directory
mkdir .python

# Change to the temporary directory
cd $TMPDIR
cp -r -t . /game-code/*

uv sync
uv pip install pyinstaller
uv run pyinstaller --onefile --add-data photos:photos --clean main.py

mv dist/main ../../output/linux/linux_game

# Go back to starting folder
cd ..

# Cleanup
sleep 5
rm -rf .python