# Per-instance LRM Memory for Players and Foes

## Summary
Introduce isolated LangChain memory objects for each player and foe instance so dialogue histories remain unique per combatant.

## Tasks
- Update `backend/plugins/players/_base.py` and `backend/plugins/foes/_base.py` to:
  - Instantiate a dedicated LangChain ChromaDB memory object for every instance rather than sharing global memory.
  - Expose async-friendly message helpers such as `async send_lrm_message(message: str) -> str` and `async receive_lrm_message(message: str) -> None` (or similar) that interact with the existing LRM interface while appending to the instance's conversation history.
  - Tie each memory object's collection name to the current run so conversation histories persist across method calls yet reset for new runs or fresh instances.
- Add unit tests covering separate histories for multiple player and foe instances.
- Sync docs:
  - Update `README.md` and `.codex/implementation/player-foe-reference.md` to note per-instance memory and new message methods.

## Context
Current LRM interactions share state across combatants, causing conversations to bleed between instances. Providing per-instance memory enables independent dialogue threads and prepares for richer NPC conversations.

## Testing
- `./run-tests.sh`
