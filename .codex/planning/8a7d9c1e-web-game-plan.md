# Web GUI and Quart Game Plan

## Goal
Transition Midori AI AutoFighter from Panda3D to a web-based architecture. The game's logic remains in Python, served through a Quart server, while the user interface runs in a separate Svelte frontend. The project no longer targets 3D rendering.

Status: ready for audit.

## Project Lead Feedback
- Use Svelte for the frontend, keeping the main menu's high-contrast icon grid inspired by Arknights.
- Use Lucide or equivalent icons with clear labels and ensure layouts scale across desktop and mobile resolutions.
- Reuse existing plugin-driven combat, menus, stat screens, and multi-room run map.
- Manage the JS frontend and Quart backend with Docker Compose.
- Keep `myunderstanding.md` current with gameplay flow updates.

## Current Issues
- Battle, shop, and rest room flows are not exposed through the web interface.
- The Svelte frontend does not yet drive these room interactions.
- Party picker and run start map display remain unfinished.
- Backend lacks tests for run state and room endpoints.
- Python Dockerfile omits required Docker tooling.

## Immediate Playable Flow
1. Expose Quart endpoints for battle, shop, and rest rooms using `save.db`.
2. Wire the Svelte UI to call these endpoints and display results.
3. Implement party picker and run start map display.
4. Add backend tests for run and room flows and update the Python Dockerfile with proper tooling.

## Detailed Plans
Detailed planning documents will be written once the playable flow is in place.
