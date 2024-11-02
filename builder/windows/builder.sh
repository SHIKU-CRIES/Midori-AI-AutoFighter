#!/bin/bash

# Create a temporary directory for the Wine prefix
TMPDIR=$(pwd)/.wine-python

# Create a Wine prefix in the temporary directory
WINEPREFIX=$TMPDIR WINEARCH=win64 winecfg /v win10

# Change to the temporary directory
cd $TMPDIR
wget "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"
cp -t . ../../../*

# Install Python into the Wine prefix
WINEPREFIX=$TMPDIR wine python-3.12.4-amd64.exe
WINEPREFIX=$TMPDIR wine python -m ensurepip
WINEPREFIX=$TMPDIR wine python -m pip install --upgrade pip
WINEPREFIX=$TMPDIR wine python -m pip install colorama pygame pyinstaller
WINEPREFIX=$TMPDIR wine pyinstaller --onefile --clean main.py

# Go back to starting folder
cd ..

# Cleanup
sleep 5
#rm -rf .wine-python