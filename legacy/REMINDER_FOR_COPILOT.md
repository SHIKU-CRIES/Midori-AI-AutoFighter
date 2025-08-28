# REMINDER FOR @copilot

## DO NOT EDIT THIS FOLDER

**IMPORTANT**: Never modify, add, or remove files in the `/legacy` folder.

This folder contains legacy code that must remain untouched. Any changes needed for compatibility or modernization should be implemented in the appropriate modern directories:

- `/backend` - for backend modifications
- `/frontend` - for frontend changes  
- `/autofighter` - for core game logic updates

## What happened before:
- I accidentally added `legacy_stats_compat.py` to this folder
- User explicitly stated not to touch legacy stuff
- Had to revert all changes to legacy folder

## Going forward:
- If legacy compatibility is needed, create bridge code in `/backend` or `/autofighter`
- Never add new files to `/legacy`
- Never modify existing files in `/legacy`
- Always respect the "do not change.txt" warning