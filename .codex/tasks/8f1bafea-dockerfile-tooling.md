# Fix backend Dockerfile tooling (`8f1bafea`)

## Summary
Bring the Python Dockerfile in line with guidelines by installing Docker and Docker Compose and splitting setup steps.

## Tasks
- Install Docker and Docker Compose in separate `RUN` steps.
- Avoid chaining commands in a single `RUN` instruction.
- Document build requirements in the backend README.

## Context
Addresses auditor findings about missing tooling and style.
