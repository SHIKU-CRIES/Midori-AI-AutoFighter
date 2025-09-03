from __future__ import annotations

import asyncio
import json
from typing import Any

from game import battle_snapshots, get_save_manager, load_map
from quart import Blueprint, jsonify, request
from routes.runs import start_run, advance_room
from routes.rooms import room_action
from routes.rewards import select_card, select_relic

bp = Blueprint("ui", __name__)


def get_default_active_run() -> str | None:
    """Get the most recent active run, or None if no runs exist."""
    try:
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else None
    except Exception:
        return None


def determine_ui_mode(game_state: dict[str, Any]) -> str:
    """Determine the current UI mode based on game state."""
    if not game_state:
        return "menu"
    
    current_state = game_state.get("current_state", {})
    room_data = current_state.get("room_data")
    
    # Check for awaiting states
    if current_state.get("awaiting_card"):
        return "card_selection"
    elif current_state.get("awaiting_relic"):
        return "relic_selection"
    elif current_state.get("awaiting_loot"):
        return "loot"
    elif current_state.get("awaiting_next"):
        return "playing"
    
    # Check for battle state
    if room_data and room_data.get("result") == "battle":
        # If battle has ended, check for reward states
        if room_data.get("ended"):
            if room_data.get("card_choices"):
                return "card_selection"
            elif room_data.get("relic_choices"):
                return "relic_selection"
            elif room_data.get("loot"):
                return "loot"
            else:
                return "playing"
        else:
            return "battle"
    
    return "playing"


def get_available_actions(mode: str, game_state: dict[str, Any]) -> list[str]:
    """Get list of available actions for the current UI mode."""
    if mode == "menu":
        return ["start_run", "load_run"]
    elif mode == "playing":
        return ["room_action", "advance_room", "end_run"]
    elif mode == "battle":
        return ["battle_snapshot", "pause_combat", "resume_combat"]
    elif mode == "card_selection":
        return ["choose_card"]
    elif mode == "relic_selection":
        return ["choose_relic"]
    elif mode == "loot":
        return ["advance_room"]
    else:
        return []


@bp.get("/ui")
async def get_ui_state() -> tuple[str, int, dict[str, Any]]:
    """Get complete UI state for the active run."""
    run_id = get_default_active_run()
    
    if not run_id:
        return jsonify({
            "mode": "menu",
            "active_run": None,
            "game_state": None,
            "available_actions": ["start_run"]
        })
    
    try:
        # Load map and party data directly (simpler than reusing get_map)
        state, rooms = await asyncio.to_thread(load_map, run_id)
        if not state:
            return jsonify({
                "mode": "menu", 
                "active_run": None,
                "game_state": None,
                "available_actions": ["start_run"]
            })

        def get_party_data():
            with get_save_manager().connection() as conn:
                cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
                row = cur.fetchone()
                return json.loads(row[0]) if row and row[0] else {}

        party_state = await asyncio.to_thread(get_party_data)

        # Determine current room state and what the frontend should display
        current_index = int(state.get("current", 0))
        current_room_data = None
        current_room_type = None
        next_room_type = None

        if rooms and 0 <= current_index < len(rooms):
            current_node = rooms[current_index]
            current_room_type = current_node.room_type

            # Get next room type if available
            if current_index + 1 < len(rooms):
                next_room_type = rooms[current_index + 1].room_type

            # Check if there's an active battle snapshot
            snap = battle_snapshots.get(run_id)
            if snap is not None and current_room_type in {'battle-weak', 'battle-normal', 'battle-boss-floor'}:
                current_room_data = snap
            elif state.get("awaiting_next"):
                # Provide basic state when awaiting next room
                current_room_data = {
                    "result": current_room_type.replace('-', '_') if current_room_type else "unknown",
                    "awaiting_next": True,
                    "current_index": current_index,
                    "current_room": current_room_type,
                    "next_room": next_room_type
                }

        game_state = {
            "map": state,
            "party": party_state.get("members", []),
            "current_state": {
                "current_index": current_index,
                "current_room_type": current_room_type,
                "next_room_type": next_room_type,
                "awaiting_next": state.get("awaiting_next", False),
                "awaiting_card": state.get("awaiting_card", False),
                "awaiting_relic": state.get("awaiting_relic", False),
                "awaiting_loot": state.get("awaiting_loot", False),
                "room_data": current_room_data
            }
        }
        
        # Determine UI mode based on game state
        mode = determine_ui_mode(game_state)
        
        return jsonify({
            "mode": mode,
            "active_run": run_id,
            "game_state": game_state,
            "available_actions": get_available_actions(mode, game_state)
        })
        
    except Exception as e:
        # If there's an error, fall back to menu mode
        return jsonify({
            "mode": "menu",
            "active_run": None, 
            "game_state": None,
            "available_actions": ["start_run"],
            "error": str(e)
        })


@bp.post("/ui/action")
async def handle_ui_action() -> tuple[str, int, dict[str, Any]]:
    """Handle UI actions and dispatch to appropriate backend functions."""
    try:
        data = await request.get_json()
        action = data.get("action")
        params = data.get("params", {})
        
        run_id = get_default_active_run()
        
        if action == "start_run":
            # Start a new run
            result = await start_run()
            return result
            
        elif action == "room_action":
            if not run_id:
                return jsonify({"error": "No active run"}), 400
            
            room_id = params.get("room_id", "0")
            result = await room_action(run_id, room_id)
            return result
            
        elif action == "advance_room":
            if not run_id:
                return jsonify({"error": "No active run"}), 400
                
            result = await advance_room(run_id)
            return result
            
        elif action == "choose_card":
            if not run_id:
                return jsonify({"error": "No active run"}), 400
                
            card_id = params.get("card_id")
            if not card_id:
                return jsonify({"error": "Missing card_id"}), 400
                
            result = await select_card(run_id)
            return result
            
        elif action == "choose_relic":
            if not run_id:
                return jsonify({"error": "No active run"}), 400
                
            relic_id = params.get("relic_id")
            if not relic_id:
                return jsonify({"error": "Missing relic_id"}), 400
                
            result = await select_relic(run_id)
            return result
            
        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Action failed: {str(e)}"}), 500