# Room View

`RoomView.svelte` displays the outcome of a room interaction. Foes are rendered
along the top row with simple health bars while party members appear on the
bottom row with small circles representing ultimate meters. Desktop and tablet
screens show up to ten foes and keep the view at a 16:9 aspect ratio. Phones
show only three foes and expand the view to fill the screen.

## Testing
- `bun test frontend/tests/api.test.js`
