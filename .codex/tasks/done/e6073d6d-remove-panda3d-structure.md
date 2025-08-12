# Remove Panda3D and Split Repo into Frontend and Backend Services

## Summary
Delete Panda3D-specific code and reorganize the repository into two services: a JavaScript frontend and a Python Quart backend for game logic. Use Docker Compose to manage both servers.

## Tasks
- Remove Panda3D modules, assets, and dependencies from the codebase.
- Create a `frontend/` directory that will house the web GUI (framework to be chosen: Vanilla, React, Vue, Svelte, Preact, Solid, or Angular).
- Create a `backend/` directory for the Quart backend and move existing gameplay logic there.
- Add a `compose.yaml` that defines separate services for the frontend and the backend.
- Ensure existing game logic remains functional through the new architecture.

## Acceptance Criteria
- No Panda3D code or references remain in the repository.
- Top-level `frontend/` and `backend/` folders exist with basic README placeholders.
- A `compose.yaml` starts both services.
- Documentation reflects the new structure and server split.
