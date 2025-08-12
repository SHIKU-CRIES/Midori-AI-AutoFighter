# Encrypted Save System

## Setup
- Uses [SQLCipher](https://www.zetetic.net/sqlcipher/) via the `sqlcipher3-binary` package.
- The backend reads `AF_DB_PATH` for the database location (defaults to `save.db` in the repository root) and `AF_DB_KEY` for the encryption key.
- Install dependencies with `uv add sqlcipher3-binary`.

## Schema
- `runs(id TEXT PRIMARY KEY, party TEXT, map TEXT)` stores the current run state.
- Additional tables for players and settings will be added as features return.

## Usage
```python
import os
from pathlib import Path

import sqlcipher3

db_path = Path(os.getenv("AF_DB_PATH", "save.db"))
key = os.getenv("AF_DB_KEY", "")

conn = sqlcipher3.connect(db_path)
conn.execute("PRAGMA key = ?", (key,))
```
Queries on `conn` transparently read and write encrypted data.

## Recovery
- Supply the same `AF_DB_KEY` to reopen the database.
- Back up both the encrypted `save.db` and any stored key material to prevent data loss.
