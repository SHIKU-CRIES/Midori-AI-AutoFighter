# Run Map

Displays a minimal vertical list of room icons beneath `aspect2d` to represent
the first floor layout. Each room uses a Lucide image from `assets/textures`
(`icon_flame` for battle, `icon_folder_open` for shop, `icon_pause` for rest,
`icon_message_square` for events, and `icon_power` for bosses). The icons are
`DirectButton` instances so the first entry can invoke `enter_first_room`
which builds a `BattleRoom` and swaps the scene.

## Testing
- `uv run pytest`
