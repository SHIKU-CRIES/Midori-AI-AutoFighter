#!/bin/bash

# Create a temporary directory for the Wine prefix
TMPDIR=$(pwd)/.wine-python

# Create a Wine prefix in the temporary directory
WINEPREFIX=$TMPDIR WINEARCH=win64 winecfg /v win10

# Change to the temporary directory
cd $TMPDIR
cp -t . ../../../*

# Install Python into the Wine prefix
WINEPREFIX=$TMPDIR winetricks --unattended powershell 

# Verify Python installation
echo 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' > builder.bat
echo 'powershell Add-Content -Path $PROFILE -Value "'"'(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression'"'"' >> builder.bat
echo 'drive_c\users\lunamidori\.cargo/bin\uv.exe sync' >> builder.bat

WINEPREFIX=$TMPDIR wine builder.bat

# Go back to starting folder
cd ..

# Cleanup
sleep 5
rm -rf .wine-python