# Loop battles and process status effects

## Summary
Battle rooms now run until every foe or party member falls. Each turn triggers `turn_start` and `turn_end` passives, then ticks all damage and healing over time effects through the new `EffectManager` before exchanging attacks.

## Testing
- `uv run pytest tests/test_card_rewards.py::test_battle_offers_choices_and_applies_effect`
