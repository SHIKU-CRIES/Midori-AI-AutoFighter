# Reviewer Mode Cheat Sheet

Quick reference for contributors auditing documentation quality.

## Key Responsibilities

- Read existing review notes in `.codex/review/` and add a new hashed note.
- Audit `.feedback/`, planning docs, notes directories, `.codex/**` instructions, `.github/` configs, and top-level `README` files.
- Record findings in a new review note with a random hash filename:

```bash
openssl rand -hex 4  # e.g., abcd1234
```

- For each issue, create a task stub in `.codex/tasks/`:

```bash
TMT-<hash>-<description>.md
```

- Do not modify code or documentation—report issues only.
- Maintain this cheat sheet with preferences collected during audits.

## Task Stub Conventions

- Prefix each task request with the responsible role:

```text
Task Master, ...
Coder, ...
Reviewer, ...
```

- Use `TMT-<hash>-<description>.md` filenames placed in `.codex/tasks/`.

## Useful Links

- Full mode guidance: [`REVIEWER.md`](../modes/REVIEWER.md)

