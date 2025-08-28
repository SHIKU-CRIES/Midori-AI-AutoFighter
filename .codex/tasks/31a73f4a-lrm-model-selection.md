# LRM Model Selection and Chat Integration

## Summary
Expose multiple language reasoning models across the app and funnel chat messages through the chosen model.

## Tasks
- **Backend configuration**
  - Create `backend/routes/config.py` with endpoints:
    - `GET /config/lrm` -> `{ current_model, available_models }` using `llms.loader.ModelName`.
    - `POST /config/lrm` -> persist `model` string in `options` table.
    - `POST /config/lrm/test` -> run the selected `model` on a provided prompt with no memory and return the raw reply.
  - Register the blueprint in `backend/app.py`.
- **Frontend settings**
  - Add `lrmModel` persistence to `frontend/src/lib/settingsStorage.js`.
  - Extend `frontend/src/lib/api.js` with `getLrmConfig()`, `setLrmModel()`, and `testLrmModel(prompt)`.
  - Update `frontend/src/lib/SettingsMenu.svelte` to display a dropdown of DeepSeek, Gemma, and GGUF models.
    - Load current model on mount via `getLrmConfig()`.
    - Save to local storage and POST to backend when changed.
    - Provide a **Test Model** button that posts a sample prompt via `testLrmModel` and shows the stateless response.
- **Chat room wiring**
  - Update `backend/autofighter/rooms/chat.py` so `resolve()` reads the persisted model, loads it via `llms.loader.load_llm`, and sends the user's message plus serialized party context. Return the model's reply as `response` alongside existing room fields.
- **Tests and docs**
  - Add/adjust frontend tests for the new settings UI and storage behavior.
  - Add backend tests covering config endpoints and ChatRoom LRM routing.
  - Sync relevant README and `.codex/implementation` docs for the new configuration and chat flow.

## Context
Players should be able to switch between available LRMs (DeepSeek, Gemma, GGUF). Both the UI and backend must honor the selection so chat rooms communicate with the selected model.

## Testing
- `./run-tests.sh`
