"""
Battle logging system for structured battle logs.

Creates organized folder structure:
/backend/logs/runs/{run_id}/battles/{battle_index}/raw/
/backend/logs/runs/{run_id}/battles/{battle_index}/summary/
"""
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading

from autofighter.stats import BUS


@dataclass
class BattleEvent:
    """Represents a single battle event."""
    timestamp: datetime
    event_type: str
    attacker_id: Optional[str]
    target_id: Optional[str]
    amount: Optional[int]
    details: Dict[str, Any] = field(default_factory=dict)
    source_type: Optional[str] = None  # attack, dot, hot, relic_effect, card_effect, etc.
    source_name: Optional[str] = None  # specific relic/card/effect name
    damage_type: Optional[str] = None  # fire, ice, light, etc.
    effect_details: Dict[str, Any] = field(default_factory=dict)  # additional effect context


@dataclass
class BattleSummary:
    """Summary statistics for a battle."""
    battle_id: str
    start_time: datetime
    end_time: Optional[datetime]
    result: str  # "victory", "defeat", "ongoing"
    party_members: List[str]
    foes: List[str]
    total_damage_dealt: Dict[str, int] = field(default_factory=dict)
    total_damage_taken: Dict[str, int] = field(default_factory=dict)
    total_healing_done: Dict[str, int] = field(default_factory=dict)
    total_hits_landed: Dict[str, int] = field(default_factory=dict)
    events: List[BattleEvent] = field(default_factory=list)
    
    # Enhanced tracking
    damage_by_source: Dict[str, Dict[str, int]] = field(default_factory=dict)  # source_type -> entity -> amount
    healing_by_source: Dict[str, Dict[str, int]] = field(default_factory=dict)  # source_type -> entity -> amount
    dot_damage: Dict[str, int] = field(default_factory=dict)  # entity -> total DoT damage dealt
    hot_healing: Dict[str, int] = field(default_factory=dict)  # entity -> total HoT healing done
    relic_effects: Dict[str, int] = field(default_factory=dict)  # relic_name -> trigger count
    card_effects: Dict[str, int] = field(default_factory=dict)  # card_name -> trigger count
    effect_applications: Dict[str, int] = field(default_factory=dict)  # effect_name -> application count


class BattleLogger:
    """Manages logging for individual battles."""
    
    def __init__(self, run_id: str, battle_index: int, base_logs_path: Optional[Path] = None):
        self.run_id = run_id
        self.battle_index = battle_index
        self.summary = BattleSummary(
            battle_id=f"{run_id}_battle_{battle_index}",
            start_time=datetime.now(),
            end_time=None,
            result="ongoing",
            party_members=[],
            foes=[]
        )
        
        # Create folder structure
        if base_logs_path is None:
            base_logs_path = Path(__file__).resolve().parent / "logs"
        self.base_path = base_logs_path / "runs" / run_id / "battles" / str(battle_index)
        self.raw_path = self.base_path / "raw"
        self.summary_path = self.base_path / "summary"
        
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.summary_path.mkdir(parents=True, exist_ok=True)
        
        # Set up raw logging
        self.raw_logger = logging.getLogger(f"battle_{run_id}_{battle_index}")
        self.raw_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers to prevent duplication
        self.raw_logger.handlers.clear()
        
        # Raw log file handler
        raw_handler = logging.FileHandler(self.raw_path / "battle.log")
        raw_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        )
        self.raw_logger.addHandler(raw_handler)
        
        # Don't propagate to root logger to avoid duplication
        self.raw_logger.propagate = False
        
        # Event tracking
        self._lock = threading.Lock()
        self._active = True
        
        # Subscribe to battle events
        self._subscribe_to_events()
        
    def _subscribe_to_events(self):
        """Subscribe to relevant battle events."""
        BUS.subscribe("battle_start", self._on_battle_start)
        BUS.subscribe("damage_dealt", self._on_damage_dealt)
        BUS.subscribe("damage_taken", self._on_damage_taken)
        BUS.subscribe("heal", self._on_heal)
        BUS.subscribe("hit_landed", self._on_hit_landed)
        BUS.subscribe("battle_end", self._on_battle_end)
        
        # Enhanced event subscriptions
        BUS.subscribe("dot_tick", self._on_dot_tick)
        BUS.subscribe("hot_tick", self._on_hot_tick)
        BUS.subscribe("relic_effect", self._on_relic_effect)
        BUS.subscribe("card_effect", self._on_card_effect)
        BUS.subscribe("effect_applied", self._on_effect_applied)
        BUS.subscribe("effect_expired", self._on_effect_expired)
        
    def _unsubscribe_from_events(self):
        """Unsubscribe from battle events."""
        BUS.unsubscribe("battle_start", self._on_battle_start)
        BUS.unsubscribe("damage_dealt", self._on_damage_dealt)
        BUS.unsubscribe("damage_taken", self._on_damage_taken)
        BUS.unsubscribe("heal", self._on_heal)
        BUS.unsubscribe("hit_landed", self._on_hit_landed)
        BUS.unsubscribe("battle_end", self._on_battle_end)
        
        # Enhanced event unsubscriptions
        BUS.unsubscribe("dot_tick", self._on_dot_tick)
        BUS.unsubscribe("hot_tick", self._on_hot_tick)
        BUS.unsubscribe("relic_effect", self._on_relic_effect)
        BUS.unsubscribe("card_effect", self._on_card_effect)
        BUS.unsubscribe("effect_applied", self._on_effect_applied)
        BUS.unsubscribe("effect_expired", self._on_effect_expired)
        
    def _log_event(self, event: BattleEvent):
        """Log an event to both raw logs and summary."""
        if not self._active:
            return
            
        with self._lock:
            # Add to summary
            self.summary.events.append(event)
            
            # Log to raw file with enhanced details
            details_str = ""
            if event.source_type:
                details_str += f" [source_type: {event.source_type}]"
            if event.source_name:
                details_str += f" [source_name: {event.source_name}]"
            if event.damage_type:
                details_str += f" [damage_type: {event.damage_type}]"
            if event.effect_details:
                details_str += f" [effect: {event.effect_details}]"
            if event.details:
                details_str += f" [details: {event.details}]"
                
            self.raw_logger.info(
                f"{event.event_type}: {event.attacker_id or 'N/A'} -> {event.target_id or 'N/A'} "
                f"(amount: {event.amount or 'N/A'}){details_str}"
            )
    
    def _on_battle_start(self, entity):
        """Handle battle start event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="battle_start",
            attacker_id=None,
            target_id=entity_id,
            amount=None,
            details={"entity_type": type(entity).__name__}
        )
        self._log_event(event)
        
        # Track entity
        if hasattr(entity, 'level'):  # Likely a foe
            if entity_id not in self.summary.foes:
                self.summary.foes.append(entity_id)
        else:  # Likely a party member
            if entity_id not in self.summary.party_members:
                self.summary.party_members.append(entity_id)
                
    def _on_damage_dealt(self, attacker, target, amount, source_type="attack", source_name=None, damage_type=None):
        """Handle damage dealt event."""
        attacker_id = getattr(attacker, 'id', str(attacker))
        target_id = getattr(target, 'id', str(target))
        
        # Get damage type if not provided
        if damage_type is None and hasattr(attacker, 'damage_type'):
            damage_type = getattr(attacker.damage_type, 'id', str(attacker.damage_type))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="damage_dealt",
            attacker_id=attacker_id,
            target_id=target_id,
            amount=amount,
            source_type=source_type,
            source_name=source_name,
            damage_type=damage_type
        )
        self._log_event(event)
        
        # Update summary stats
        self.summary.total_damage_dealt[attacker_id] = self.summary.total_damage_dealt.get(attacker_id, 0) + amount
        
        # Track damage by source type
        if source_type not in self.summary.damage_by_source:
            self.summary.damage_by_source[source_type] = {}
        self.summary.damage_by_source[source_type][attacker_id] = self.summary.damage_by_source[source_type].get(attacker_id, 0) + amount
        
    def _on_damage_taken(self, target, attacker, amount):
        """Handle damage taken event."""
        attacker_id = getattr(attacker, 'id', str(attacker)) if attacker else None
        target_id = getattr(target, 'id', str(target))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="damage_taken",
            attacker_id=attacker_id,
            target_id=target_id,
            amount=amount
        )
        self._log_event(event)
        
        # Update summary stats
        self.summary.total_damage_taken[target_id] = self.summary.total_damage_taken.get(target_id, 0) + amount
        
    def _on_heal(self, healer, target, amount, source_type="heal", source_name=None):
        """Handle healing event."""
        healer_id = getattr(healer, 'id', str(healer)) if healer else None
        target_id = getattr(target, 'id', str(target))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="heal",
            attacker_id=healer_id,
            target_id=target_id,
            amount=amount,
            source_type=source_type,
            source_name=source_name
        )
        self._log_event(event)
        
        # Update summary stats
        if healer_id:
            self.summary.total_healing_done[healer_id] = self.summary.total_healing_done.get(healer_id, 0) + amount
            
            # Track healing by source type
            if source_type not in self.summary.healing_by_source:
                self.summary.healing_by_source[source_type] = {}
            self.summary.healing_by_source[source_type][healer_id] = self.summary.healing_by_source[source_type].get(healer_id, 0) + amount
            
    def _on_hit_landed(self, attacker, target, amount, source_type="attack", source_name=None):
        """Handle hit landed event."""
        attacker_id = getattr(attacker, 'id', str(attacker))
        target_id = getattr(target, 'id', str(target))
        
        # Get damage type if available
        damage_type = None
        if hasattr(attacker, 'damage_type'):
            damage_type = getattr(attacker.damage_type, 'id', str(attacker.damage_type))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="hit_landed",
            attacker_id=attacker_id,
            target_id=target_id,
            amount=amount,
            source_type=source_type,
            source_name=source_name,
            damage_type=damage_type
        )
        self._log_event(event)
        
        # Update summary stats
        self.summary.total_hits_landed[attacker_id] = self.summary.total_hits_landed.get(attacker_id, 0) + 1
        
    def _on_battle_end(self, entity):
        """Handle battle end event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="battle_end",
            attacker_id=None,
            target_id=entity_id,
            amount=None,
            details={"entity_type": type(entity).__name__}
        )
        self._log_event(event)
        
    def _on_dot_tick(self, attacker, target, amount, dot_name=None, effect_details=None):
        """Handle DoT tick event."""
        attacker_id = getattr(attacker, 'id', str(attacker))
        target_id = getattr(target, 'id', str(target))
        
        # Get damage type if available
        damage_type = None
        if hasattr(attacker, 'damage_type'):
            damage_type = getattr(attacker.damage_type, 'id', str(attacker.damage_type))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="dot_tick",
            attacker_id=attacker_id,
            target_id=target_id,
            amount=amount,
            source_type="dot",
            source_name=dot_name,
            damage_type=damage_type,
            effect_details=effect_details or {}
        )
        self._log_event(event)
        
        # Update DoT damage tracking
        self.summary.dot_damage[attacker_id] = self.summary.dot_damage.get(attacker_id, 0) + amount
        
    def _on_hot_tick(self, healer, target, amount, hot_name=None, effect_details=None):
        """Handle HoT tick event."""
        healer_id = getattr(healer, 'id', str(healer)) if healer else None
        target_id = getattr(target, 'id', str(target))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="hot_tick",
            attacker_id=healer_id,
            target_id=target_id,
            amount=amount,
            source_type="hot",
            source_name=hot_name,
            effect_details=effect_details or {}
        )
        self._log_event(event)
        
        # Update HoT healing tracking
        if healer_id:
            self.summary.hot_healing[healer_id] = self.summary.hot_healing.get(healer_id, 0) + amount
            
    def _on_relic_effect(self, relic_name, entity, effect_type=None, amount=None, details=None):
        """Handle relic effect event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="relic_effect",
            attacker_id=entity_id,
            target_id=entity_id,
            amount=amount,
            source_type="relic_effect",
            source_name=relic_name,
            effect_details=details or {"effect_type": effect_type}
        )
        self._log_event(event)
        
        # Update relic effect tracking
        self.summary.relic_effects[relic_name] = self.summary.relic_effects.get(relic_name, 0) + 1
        
    def _on_card_effect(self, card_name, entity, effect_type=None, amount=None, details=None):
        """Handle card effect event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="card_effect",
            attacker_id=entity_id,
            target_id=entity_id,
            amount=amount,
            source_type="card_effect",
            source_name=card_name,
            effect_details=details or {"effect_type": effect_type}
        )
        self._log_event(event)
        
        # Update card effect tracking
        self.summary.card_effects[card_name] = self.summary.card_effects.get(card_name, 0) + 1
        
    def _on_effect_applied(self, effect_name, entity, details=None):
        """Handle effect application event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="effect_applied",
            attacker_id=None,
            target_id=entity_id,
            amount=None,
            source_type="effect",
            source_name=effect_name,
            effect_details=details or {}
        )
        self._log_event(event)
        
        # Update effect application tracking
        self.summary.effect_applications[effect_name] = self.summary.effect_applications.get(effect_name, 0) + 1
        
    def _on_effect_expired(self, effect_name, entity, details=None):
        """Handle effect expiration event."""
        entity_id = getattr(entity, 'id', str(entity))
        
        event = BattleEvent(
            timestamp=datetime.now(),
            event_type="effect_expired",
            attacker_id=None,
            target_id=entity_id,
            amount=None,
            source_type="effect",
            source_name=effect_name,
            effect_details=details or {}
        )
        self._log_event(event)
        
    def finalize_battle(self, result: str = "completed"):
        """Finalize the battle and write summary."""
        if not self._active:
            return
            
        with self._lock:
            self.summary.end_time = datetime.now()
            self.summary.result = result
            
            # Write summary to JSON
            summary_data = {
                "battle_id": self.summary.battle_id,
                "start_time": self.summary.start_time.isoformat(),
                "end_time": self.summary.end_time.isoformat() if self.summary.end_time else None,
                "result": self.summary.result,
                "party_members": self.summary.party_members,
                "foes": self.summary.foes,
                "total_damage_dealt": self.summary.total_damage_dealt,
                "total_damage_taken": self.summary.total_damage_taken,
                "total_healing_done": self.summary.total_healing_done,
                "total_hits_landed": self.summary.total_hits_landed,
                "event_count": len(self.summary.events),
                "duration_seconds": (
                    (self.summary.end_time - self.summary.start_time).total_seconds()
                    if self.summary.end_time else None
                ),
                # Enhanced tracking data
                "damage_by_source": self.summary.damage_by_source,
                "healing_by_source": self.summary.healing_by_source,
                "dot_damage": self.summary.dot_damage,
                "hot_healing": self.summary.hot_healing,
                "relic_effects": self.summary.relic_effects,
                "card_effects": self.summary.card_effects,
                "effect_applications": self.summary.effect_applications
            }
            
            # Write summary JSON
            with open(self.summary_path / "battle_summary.json", "w") as f:
                json.dump(summary_data, f, indent=2)
                
            # Write detailed events
            events_data = [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "attacker_id": event.attacker_id,
                    "target_id": event.target_id,
                    "amount": event.amount,
                    "details": event.details,
                    "source_type": event.source_type,
                    "source_name": event.source_name,
                    "damage_type": event.damage_type,
                    "effect_details": event.effect_details
                }
                for event in self.summary.events
            ]
            
            with open(self.summary_path / "events.json", "w") as f:
                json.dump(events_data, f, indent=2)
                
            # Write human-readable summary
            self._write_human_summary()
            
            # Cleanup
            self._unsubscribe_from_events()
            self._active = False
            
            # Close raw log handlers
            for handler in self.raw_logger.handlers:
                handler.close()
            self.raw_logger.handlers.clear()
    
    def _write_human_summary(self):
        """Write a human-readable summary."""
        duration = (
            (self.summary.end_time - self.summary.start_time).total_seconds()
            if self.summary.end_time else 0
        )
        
        lines = [
            f"Battle Summary: {self.summary.battle_id}",
            f"{'=' * 50}",
            f"Result: {self.summary.result.upper()}",
            f"Duration: {duration:.1f} seconds",
            f"Start: {self.summary.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"End: {self.summary.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.summary.end_time else 'N/A'}",
            "",
            f"Participants:",
            f"  Party: {', '.join(self.summary.party_members) if self.summary.party_members else 'None'}",
            f"  Foes: {', '.join(self.summary.foes) if self.summary.foes else 'None'}",
            "",
            "Damage Dealt:",
        ]
        
        for entity, damage in sorted(self.summary.total_damage_dealt.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {entity}: {damage}")
            
        lines.extend([
            "",
            "Damage Taken:",
        ])
        
        for entity, damage in sorted(self.summary.total_damage_taken.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {entity}: {damage}")
            
        if self.summary.total_healing_done:
            lines.extend([
                "",
                "Healing Done:",
            ])
            for entity, healing in sorted(self.summary.total_healing_done.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {entity}: {healing}")
                
        lines.extend([
            "",
            "Hits Landed:",
        ])
        
        for entity, hits in sorted(self.summary.total_hits_landed.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {entity}: {hits}")
            
        # Enhanced tracking summaries
        if self.summary.damage_by_source:
            lines.extend([
                "",
                "Damage by Source Type:",
            ])
            for source_type, entities in self.summary.damage_by_source.items():
                lines.append(f"  {source_type.upper()}:")
                for entity, damage in sorted(entities.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"    {entity}: {damage}")
                    
        if self.summary.healing_by_source:
            lines.extend([
                "",
                "Healing by Source Type:",
            ])
            for source_type, entities in self.summary.healing_by_source.items():
                lines.append(f"  {source_type.upper()}:")
                for entity, healing in sorted(entities.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"    {entity}: {healing}")
                    
        if self.summary.dot_damage:
            lines.extend([
                "",
                "DoT Damage Dealt:",
            ])
            for entity, damage in sorted(self.summary.dot_damage.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {entity}: {damage}")
                
        if self.summary.hot_healing:
            lines.extend([
                "",
                "HoT Healing Done:",
            ])
            for entity, healing in sorted(self.summary.hot_healing.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {entity}: {healing}")
                
        if self.summary.relic_effects:
            lines.extend([
                "",
                "Relic Effects Triggered:",
            ])
            for relic, count in sorted(self.summary.relic_effects.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {relic}: {count} times")
                
        if self.summary.card_effects:
            lines.extend([
                "",
                "Card Effects Triggered:",
            ])
            for card, count in sorted(self.summary.card_effects.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {card}: {count} times")
                
        if self.summary.effect_applications:
            lines.extend([
                "",
                "Effects Applied:",
            ])
            for effect, count in sorted(self.summary.effect_applications.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {effect}: {count} times")
            
        lines.extend([
            "",
            f"Total Events: {len(self.summary.events)}",
        ])
        
        with open(self.summary_path / "human_summary.txt", "w") as f:
            f.write("\n".join(lines))


class RunLogger:
    """Manages logging for an entire run."""
    
    def __init__(self, run_id: str, base_logs_path: Optional[Path] = None):
        self.run_id = run_id
        self.battle_count = 0
        self.current_battle_logger: Optional[BattleLogger] = None
        self.base_logs_path = base_logs_path
        
        # Create run folder
        if base_logs_path is None:
            base_logs_path = Path(__file__).resolve().parent / "logs"
        self.run_path = base_logs_path / "runs" / run_id
        self.run_path.mkdir(parents=True, exist_ok=True)
        
    def start_battle(self) -> BattleLogger:
        """Start logging a new battle."""
        if self.current_battle_logger:
            self.current_battle_logger.finalize_battle("interrupted")
            
        self.battle_count += 1
        self.current_battle_logger = BattleLogger(self.run_id, self.battle_count, self.base_logs_path)
        return self.current_battle_logger
        
    def end_battle(self, result: str = "completed"):
        """End the current battle."""
        if self.current_battle_logger:
            self.current_battle_logger.finalize_battle(result)
            self.current_battle_logger = None
            
    def finalize_run(self):
        """Finalize the entire run."""
        if self.current_battle_logger:
            self.current_battle_logger.finalize_battle("run_ended")
            self.current_battle_logger = None


# Global run logger instance
_current_run_logger: Optional[RunLogger] = None
_run_logger_lock = threading.Lock()


def start_run_logging(run_id: str) -> RunLogger:
    """Start logging for a new run."""
    global _current_run_logger
    with _run_logger_lock:
        if _current_run_logger:
            _current_run_logger.finalize_run()
        _current_run_logger = RunLogger(run_id)
        return _current_run_logger


def get_current_run_logger() -> Optional[RunLogger]:
    """Get the current run logger."""
    return _current_run_logger


def end_run_logging():
    """End logging for the current run."""
    global _current_run_logger
    with _run_logger_lock:
        if _current_run_logger:
            _current_run_logger.finalize_run()
            _current_run_logger = None


def start_battle_logging() -> Optional[BattleLogger]:
    """Start logging for a new battle."""
    if _current_run_logger:
        return _current_run_logger.start_battle()
    return None


def end_battle_logging(result: str = "completed"):
    """End logging for the current battle."""
    if _current_run_logger:
        _current_run_logger.end_battle(result)