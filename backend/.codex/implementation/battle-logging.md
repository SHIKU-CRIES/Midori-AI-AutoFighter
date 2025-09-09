# Battle Logging System

The battle logging system provides structured, organized logging for battles with detailed summaries and organized folder structures.

## Folder Structure

```
backend/logs/runs/{run_id}/battles/{battle_index}/
├── raw/
│   └── battle.log              # Raw battle events log
└── summary/
    ├── battle_summary.json     # Summary statistics in JSON format
    ├── events.json            # Detailed events list in JSON format
    └── human_summary.txt      # Human-readable summary
```

## Features

### Automatic Event Tracking
The system automatically tracks:
- `battle_start` - When battles begin
- `damage_dealt` - When damage is dealt
- `damage_taken` - When damage is taken  
- `heal` - When healing occurs
- `hit_landed` - When successful hits occur
- `battle_end` - When battles end

### Summary Statistics
Each battle summary includes:
- Total damage dealt by each participant
- Total damage taken by each participant
- Total healing done by each participant
- Total hits landed by each participant
- Total self-inflicted damage by each participant
- Total friendly fire damage by each participant
- Battle duration and result
- Participant lists (party members and foes)
- Damage totals by element for each combatant

### Usage

The system is automatically integrated into the battle flow:

1. **Run starts**: `start_run_logging(run_id)` is called when a new run begins
2. **Battle starts**: `start_battle_logging()` is called once after the party and foes are determined, before any battle events
3. **Battle ends**: `end_battle_logging(result)` is called when a battle ends
4. **Run ends**: `end_run_logging()` is called when a run ends

### Event Bus Integration

The battle logging system subscribes to the global event bus and automatically captures relevant events. It integrates seamlessly with existing game mechanics without requiring code changes to emit events manually.

### File Formats

#### battle_summary.json
```json
{
  "battle_id": "run_123_battle_1",
  "start_time": "2024-08-29T00:18:45.123456",
  "end_time": "2024-08-29T00:19:12.654321",
  "result": "victory",
  "party_members": ["player", "ally1"],
  "foes": ["goblin", "orc"],
  "total_damage_dealt": {
    "player": 250,
    "ally1": 180
  },
  "total_damage_taken": {
    "player": 50,
    "ally1": 75
  },
  "total_healing_done": {
    "player": 100
  },
  "total_hits_landed": {
    "player": 8,
    "ally1": 6
  },
  "self_damage": {
    "player": 5
  },
  "friendly_fire": {
    "player": 12
  },
  "event_count": 45,
  "duration_seconds": 27.5
}
```

#### events.json
```json
[
  {
    "timestamp": "2024-08-29T00:18:45.123456",
    "event_type": "battle_start",
    "attacker_id": null,
    "target_id": "player",
    "amount": null,
    "details": {"entity_type": "Stats"}
  },
  {
    "timestamp": "2024-08-29T00:18:45.234567",
    "event_type": "damage_dealt",
    "attacker_id": "player",
    "target_id": "goblin",
    "amount": 45,
    "details": {}
  }
]
```

#### human_summary.txt
```
Battle Summary: run_123_battle_1
==================================================
Result: VICTORY
Duration: 27.5 seconds
Start: 2024-08-29 00:18:45
End: 2024-08-29 00:19:12

Participants:
  Party: player, ally1
  Foes: goblin, orc

Damage Dealt:
  player: 250
  ally1: 180

Damage Taken:
  player: 50
  ally1: 75

Healing Done:
  player: 100

Hits Landed:
  player: 8
  ally1: 6

Total Events: 45
```

## Implementation Notes

- Uses an async-friendly queue and timed memory buffer so log writes happen off the event loop and flush to disk roughly every 15 seconds or when a battle ends
- Automatically creates directory structure as needed
- Integrates with existing event bus system
- Does not interfere with existing logging to `backend.log`
- Logs are organized by run ID and battle index for easy navigation
- Each battle gets its own logger instance to prevent interference
- Call `start_battle_logging()` only once per battle after participants are set; additional calls finalize the previous battle as "interrupted"

## Battle Review API

The latest battle summary can be fetched using:

```
GET /run/<run_id>/battles/<index>/summary
```

This endpoint returns the `battle_summary.json` data, enabling clients to
render post-battle review screens with per-element damage breakdowns.
