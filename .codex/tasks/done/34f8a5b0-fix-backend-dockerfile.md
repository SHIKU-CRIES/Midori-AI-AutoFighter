# Fix backend Dockerfile (`34f8a5b0`)

## Summary
Address review feedback for `Dockerfile.python`.

## Tasks
 - Install Docker and Docker Compose inside the image.
 - Split environment setup for `/.venv` into three separate `RUN` lines.
 - Verify `UV_EXTRA` build argument still functions.
 - Document the changes in the backend README.

## Context
Reviewer noted missing tooling and combined commands in the existing Dockerfile.
