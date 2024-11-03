#!/bin/bash

# Create a temporary directory for the Wine prefix
TMPDIR=$(pwd)/.wine-python

# Create a Wine prefix in the temporary directory
WINEPREFIX=$TMPDIR WINEARCH=win64 winecfg /v win10

# Change to the temporary directory
cd $TMPDIR
wget "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
cp -t . /game-code/*

# Install Python into the Wine prefix
WINEPREFIX=$TMPDIR xvfb-run wine python-3.12.7-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
WINEPREFIX=$TMPDIR xvfb-run wine python -m ensurepip
WINEPREFIX=$TMPDIR xvfb-run wine python -m pip install --upgrade pip
WINEPREFIX=$TMPDIR xvfb-run wine python -m pip install colorama pygame pyinstaller
WINEPREFIX=$TMPDIR xvfb-run wine pyinstaller --onefile --clean main.py

mv dist/main.exe ../../output/windows_game.exe

# Go back to starting folder
cd ..

# Cleanup
sleep 5
rm -rf .wine-python