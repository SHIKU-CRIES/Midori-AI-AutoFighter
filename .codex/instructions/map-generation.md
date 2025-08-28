# Map Generation

Define floor layouts with deterministic seeding. Floors contain 45 rooms by default with a final `battle_boss_floor` node. At least two `shop` and two `rest` rooms are inserted, and extra rooms or boss nodes appear as Pressure Level rises. Chat rooms are flagged to appear after battle rooms without increasing the room count.

Use `MapGenerator` to build room lists and `render_floor` for a simple text preview during development.
