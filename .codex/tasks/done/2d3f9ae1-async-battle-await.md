# Make battle loop async-friendly

## Summary
BattleRoom now awaits between turn pairs so battles yield to the event loop, triggers `battle_end` passives for all combatants, and keeps cards, relics, and DoT/HoT effects active until either the foe or the party falls.

## Testing
- `uv run pytest` (KeyboardInterrupt during run)
- `uv run pytest tests/test_card_rewards.py::test_battle_offers_choices_and_applies_effect -q`
- `uv run pytest tests/test_shop_room.py::test_shop_room_heals_and_tracks_inventory -q`
- `bun test`
