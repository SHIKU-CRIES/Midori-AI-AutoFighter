# Event and Chat Rooms

## Event Room
- Present a text prompt with multiple selectable options.
- Outcomes modify player `Stats` or inventory via deterministic, seeded randomness.
- Events triggered after battles do not consume the floor's room count.

### Event Plugins
- Store event modules under `plugins/events/`.
- Declare `plugin_type = "event"` and provide a `build(seed: int | None = None)` method returning an `autofighter.event_room.Event`.
- `PluginLoader` discovers these builders; `EventRoom` randomly selects one when no event is supplied.

## Chat Room
- Allows the player to send exactly one message to an LLM-driven character.
- Responses are currently placeholders; integrate real models under `llms/` in the future.
- Usage is limited to six chats per floor; further rooms should not spawn once the limit is reached.
