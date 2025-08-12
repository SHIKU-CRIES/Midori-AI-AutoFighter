# Run Map

`RunMap.svelte` renders the floor layout returned by the Quart backend. The map
prop is an array of room identifiers such as `start`, `battle`, and `boss`. The
component displays these entries as a horizontal list of buttons and emits a
`select` event with the chosen room. The main page listens for this event and
calls the matching room endpoint, rendering a `RoomView` with the results.

## Testing
- `bun test frontend/tests/runmap.test.js`
