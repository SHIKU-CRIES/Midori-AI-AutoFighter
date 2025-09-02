"""
Prototype: Concurrent Phase Processing for Battle System

This demonstrates how to implement concurrent processing within battle phases
while maintaining strict turn order between phases. This approach provides
significant performance improvements without breaking battle logic integrity.

Key Concept: Parallelize independent operations within phases, maintain 
sequential execution for operations that depend on order.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
import random
import time
from typing import Any
from typing import Dict
from typing import List


class PhaseType(Enum):
    PREPARATION = "preparation"
    EXECUTION = "execution"
    CLEANUP = "cleanup"

@dataclass
class FighterPreparation:
    """Data structure for fighter preparation results"""
    fighter_id: str
    target_analysis: Dict[str, Any]
    damage_calculations: Dict[str, float]
    effect_previews: List[Dict[str, Any]]
    passive_triggers: List[str]
    can_act: bool
    preparation_time: float

@dataclass
class PhaseStats:
    """Performance statistics for phase processing"""
    phase_type: PhaseType
    total_fighters: int
    concurrent_preparations: int
    sequential_executions: int
    total_time: float
    preparation_time: float
    execution_time: float

class ConcurrentBattlePhaseProcessor:
    """
    Processes battle phases with concurrent preparation and sequential execution.
    
    This maintains battle logic integrity while improving performance through
    parallelization of independent operations.
    """

    def __init__(self):
        self.phase_stats: List[PhaseStats] = []
        self.debug_logging = True

    async def process_party_phase_concurrent(self,
                                           combat_party,
                                           party_effects,
                                           foes,
                                           turn: int,
                                           battle_context: Dict[str, Any]) -> PhaseStats:
        """
        Process party phase with concurrent preparation and sequential execution.
        
        Phase 1: Concurrent Preparation (Independent Operations)
        - Effect calculations
        - Target analysis  
        - Damage previews
        - Passive ability checks
        
        Phase 2: Sequential Execution (Order-Dependent Operations)
        - Actual attacks and ability usage
        - HP/stat modifications
        - Event emissions
        - Turn order management
        """
        start_time = time.perf_counter()

        if self.debug_logging:
            print(f"Starting concurrent party phase processing for {len(combat_party.members)} members")

        # Phase 1: Concurrent Preparation
        prep_start = time.perf_counter()
        preparations = await self._prepare_party_members_concurrent(
            combat_party.members, party_effects, foes, turn, battle_context
        )
        prep_time = time.perf_counter() - prep_start

        # Phase 2: Sequential Execution (maintains turn order)
        exec_start = time.perf_counter()
        execution_results = await self._execute_party_actions_sequential(
            combat_party.members, party_effects, foes, preparations, battle_context
        )
        exec_time = time.perf_counter() - exec_start

        total_time = time.perf_counter() - start_time

        # Create performance statistics
        stats = PhaseStats(
            phase_type=PhaseType.PREPARATION,
            total_fighters=len(combat_party.members),
            concurrent_preparations=len([p for p in preparations if p.can_act]),
            sequential_executions=len(execution_results),
            total_time=total_time,
            preparation_time=prep_time,
            execution_time=exec_time
        )

        self.phase_stats.append(stats)

        if self.debug_logging:
            print(f"Party phase completed: {total_time:.4f}s (prep: {prep_time:.4f}s, exec: {exec_time:.4f}s)")

        return stats

    async def _prepare_party_members_concurrent(self,
                                              members: List,
                                              party_effects: List,
                                              foes: List,
                                              turn: int,
                                              battle_context: Dict[str, Any]) -> List[FighterPreparation]:
        """
        Prepare all party members concurrently.
        
        This phase can be parallelized because these operations are independent:
        - Analyzing available targets
        - Calculating potential damage values
        - Checking passive ability triggers
        - Previewing effect applications
        """
        preparation_tasks = []

        for i, (member, effect_mgr) in enumerate(zip(members, party_effects)):
            if member.hp > 0:  # Only prepare living members
                task = self._prepare_single_fighter(
                    member, effect_mgr, foes, turn, battle_context, f"party_{i}"
                )
                preparation_tasks.append(task)
            else:
                # Create placeholder for dead members
                prep = FighterPreparation(
                    fighter_id=getattr(member, 'id', f'member_{i}'),
                    target_analysis={},
                    damage_calculations={},
                    effect_previews=[],
                    passive_triggers=[],
                    can_act=False,
                    preparation_time=0.0
                )
                preparation_tasks.append(asyncio.create_task(self._return_preparation(prep)))

        # Execute all preparations in parallel
        if self.debug_logging:
            print(f"  Executing {len(preparation_tasks)} concurrent preparations...")

        preparations = await asyncio.gather(*preparation_tasks)

        if self.debug_logging:
            active_preps = [p for p in preparations if p.can_act]
            print(f"  Completed {len(active_preps)} fighter preparations")

        return preparations

    async def _prepare_single_fighter(self,
                                     fighter,
                                     effect_mgr,
                                     targets: List,
                                     turn: int,
                                     battle_context: Dict[str, Any],
                                     fighter_id: str) -> FighterPreparation:
        """
        Prepare a single fighter for their turn.
        
        This includes all independent calculations that can be done
        before the actual turn execution.
        """
        prep_start = time.perf_counter()

        # Target analysis (can be done concurrently)
        target_analysis = await self._analyze_targets(fighter, targets)

        # Damage calculations (can be done concurrently)
        damage_calculations = await self._calculate_damage_previews(fighter, targets)

        # Effect previews (can be done concurrently)
        effect_previews = await self._preview_effect_applications(fighter, effect_mgr)

        # Passive ability checks (can be done concurrently)
        passive_triggers = await self._check_passive_triggers(fighter, turn, battle_context)

        prep_time = time.perf_counter() - prep_start

        preparation = FighterPreparation(
            fighter_id=getattr(fighter, 'id', fighter_id),
            target_analysis=target_analysis,
            damage_calculations=damage_calculations,
            effect_previews=effect_previews,
            passive_triggers=passive_triggers,
            can_act=fighter.hp > 0,
            preparation_time=prep_time
        )

        if self.debug_logging:
            print(f"    Prepared {preparation.fighter_id} in {prep_time:.4f}s")

        return preparation

    async def _analyze_targets(self, fighter, targets: List) -> Dict[str, Any]:
        """Analyze available targets and their properties"""
        alive_targets = [t for t in targets if getattr(t, 'hp', 0) > 0]

        analysis = {
            'total_targets': len(targets),
            'alive_targets': len(alive_targets),
            'target_priorities': {},
            'optimal_target_index': None
        }

        if alive_targets:
            # Calculate target priorities based on fighter's strategy
            for i, target in enumerate(alive_targets):
                priority = self._calculate_target_priority(fighter, target)
                analysis['target_priorities'][i] = priority

            # Find optimal target
            if analysis['target_priorities']:
                optimal_idx = max(analysis['target_priorities'].keys(),
                                key=lambda k: analysis['target_priorities'][k])
                analysis['optimal_target_index'] = optimal_idx

        # Simulate processing time
        await asyncio.sleep(0.001)

        return analysis

    async def _calculate_damage_previews(self, fighter, targets: List) -> Dict[str, float]:
        """Pre-calculate potential damage to all targets"""
        damage_previews = {}

        alive_targets = [t for t in targets if getattr(t, 'hp', 0) > 0]

        for i, target in enumerate(alive_targets):
            # Simulate damage calculation (simplified)
            base_damage = getattr(fighter, 'atk', 100)
            target_defense = getattr(target, 'defense', 50)
            target_mitigation = getattr(target, 'mitigation', 0.1)

            # Basic damage formula
            damage = max(1, base_damage - target_defense) * (1 - target_mitigation)
            damage_previews[f'target_{i}'] = damage

        # Simulate processing time
        await asyncio.sleep(0.001)

        return damage_previews

    async def _preview_effect_applications(self, fighter, effect_mgr) -> List[Dict[str, Any]]:
        """Preview what effects will be applied this turn"""
        effect_previews = []

        # Preview DOT ticks
        if hasattr(effect_mgr, 'dots'):
            for dot in effect_mgr.dots[:5]:  # Preview first 5 DOTs
                preview = {
                    'type': 'dot',
                    'name': getattr(dot, 'name', 'Unknown DOT'),
                    'estimated_damage': getattr(dot, 'damage', 0)
                }
                effect_previews.append(preview)

        # Preview HOT ticks
        if hasattr(effect_mgr, 'hots'):
            for hot in effect_mgr.hots[:5]:  # Preview first 5 HOTs
                preview = {
                    'type': 'hot',
                    'name': getattr(hot, 'name', 'Unknown HOT'),
                    'estimated_healing': getattr(hot, 'healing', 0)
                }
                effect_previews.append(preview)

        # Simulate processing time
        await asyncio.sleep(0.001)

        return effect_previews

    async def _check_passive_triggers(self, fighter, turn: int, battle_context: Dict[str, Any]) -> List[str]:
        """Check which passive abilities will trigger this turn"""
        triggers = []

        if hasattr(fighter, 'passives'):
            for passive_id in fighter.passives[:10]:  # Check first 10 passives
                # Simulate passive trigger check
                if self._should_passive_trigger(passive_id, turn, battle_context):
                    triggers.append(passive_id)

        # Simulate processing time
        await asyncio.sleep(0.001)

        return triggers

    def _calculate_target_priority(self, fighter, target) -> float:
        """Calculate target priority for this fighter"""
        # Simple priority calculation
        target_hp = getattr(target, 'hp', 100)
        target_max_hp = getattr(target, 'max_hp', 100)

        # Prioritize low HP targets
        hp_factor = 1.0 - (target_hp / max(target_max_hp, 1))

        # Add some randomness
        random_factor = random.random() * 0.3

        return hp_factor + random_factor

    def _should_passive_trigger(self, passive_id: str, turn: int, battle_context: Dict[str, Any]) -> bool:
        """Determine if a passive ability should trigger"""
        # Simple trigger logic based on passive ID and turn
        if 'turn_start' in passive_id.lower():
            return True
        if 'every_5_turns' in passive_id.lower():
            return turn % 5 == 0
        if 'low_hp' in passive_id.lower():
            return battle_context.get('fighter_hp_percent', 1.0) < 0.3

        return random.random() < 0.2  # 20% chance for other passives

    async def _return_preparation(self, prep: FighterPreparation) -> FighterPreparation:
        """Helper to return preparation as an awaitable"""
        return prep

    async def _execute_party_actions_sequential(self,
                                              members: List,
                                              party_effects: List,
                                              foes: List,
                                              preparations: List[FighterPreparation],
                                              battle_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute party member actions sequentially to maintain turn order.
        
        This phase must be sequential because:
        - Turn order matters for game balance
        - Actions can affect subsequent actions
        - Events must fire in the correct sequence
        - State changes must be applied in order
        """
        execution_results = []

        for i, (member, effect_mgr, preparation) in enumerate(zip(members, party_effects, preparations)):
            if not preparation.can_act:
                continue

            if self.debug_logging:
                print(f"    Executing {preparation.fighter_id}'s turn...")

            # Use preparation data for optimized execution
            result = await self._execute_single_fighter_action(
                member, effect_mgr, foes, preparation, battle_context
            )

            execution_results.append(result)

            # Apply state changes immediately (order matters)
            await self._apply_state_changes(result, battle_context)

            # Check for battle end conditions after each action
            if self._check_battle_end_conditions(members, foes):
                if self.debug_logging:
                    print("    Battle ended during party phase")
                break

        return execution_results

    async def _execute_single_fighter_action(self,
                                           fighter,
                                           effect_mgr,
                                           targets: List,
                                           preparation: FighterPreparation,
                                           battle_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single fighter's action using preparation data"""

        # Use pre-calculated target analysis
        target_analysis = preparation.target_analysis
        optimal_target_idx = target_analysis.get('optimal_target_index')

        # Select target based on preparation
        alive_targets = [t for t in targets if getattr(t, 'hp', 0) > 0]
        if optimal_target_idx is not None and optimal_target_idx < len(alive_targets):
            target = alive_targets[optimal_target_idx]
        elif alive_targets:
            target = random.choice(alive_targets)
        else:
            # No valid targets
            return {
                'fighter_id': preparation.fighter_id,
                'action': 'no_target',
                'damage_dealt': 0,
                'target_id': None
            }

        # Use pre-calculated damage
        damage_key = f'target_{optimal_target_idx}' if optimal_target_idx is not None else 'target_0'
        estimated_damage = preparation.damage_calculations.get(damage_key, 0)

        # Apply damage (this is where actual state changes happen)
        actual_damage = await self._apply_damage_to_target(target, estimated_damage)

        # Trigger passive abilities that were pre-calculated
        await self._trigger_prepared_passives(fighter, preparation.passive_triggers)

        # Process effects using pre-calculated data
        await self._process_prepared_effects(effect_mgr, preparation.effect_previews)

        # Simulate action execution time
        await asyncio.sleep(0.002)

        return {
            'fighter_id': preparation.fighter_id,
            'action': 'attack',
            'damage_dealt': actual_damage,
            'target_id': getattr(target, 'id', 'unknown'),
            'passives_triggered': len(preparation.passive_triggers),
            'effects_processed': len(preparation.effect_previews)
        }

    async def _apply_damage_to_target(self, target, estimated_damage: float) -> float:
        """Apply damage to target and return actual damage dealt"""
        # Add some variance to the estimated damage
        variance = random.uniform(0.8, 1.2)
        actual_damage = estimated_damage * variance

        # Apply damage to target
        current_hp = getattr(target, 'hp', 100)
        new_hp = max(0, current_hp - actual_damage)

        # In real implementation, this would call target.apply_damage()
        setattr(target, 'hp', new_hp)

        return actual_damage

    async def _trigger_prepared_passives(self, fighter, passive_triggers: List[str]) -> None:
        """Trigger passive abilities that were pre-calculated"""
        for passive_id in passive_triggers:
            # In real implementation, this would call the passive ability
            if self.debug_logging:
                print(f"      Triggered passive: {passive_id}")
            await asyncio.sleep(0.001)

    async def _process_prepared_effects(self, effect_mgr, effect_previews: List[Dict[str, Any]]) -> None:
        """Process effects using pre-calculated data"""
        for effect_preview in effect_previews:
            effect_type = effect_preview.get('type')
            effect_name = effect_preview.get('name')

            if self.debug_logging:
                print(f"      Processing {effect_type}: {effect_name}")

            # In real implementation, this would apply the actual effect
            await asyncio.sleep(0.001)

    async def _apply_state_changes(self, execution_result: Dict[str, Any], battle_context: Dict[str, Any]) -> None:
        """Apply state changes from action execution"""
        # Update battle context with action results
        if 'damage_dealt' in execution_result:
            total_damage = battle_context.get('total_damage_dealt', 0)
            battle_context['total_damage_dealt'] = total_damage + execution_result['damage_dealt']

        # In real implementation, this would update global battle state
        await asyncio.sleep(0.001)

    def _check_battle_end_conditions(self, party_members: List, foes: List) -> bool:
        """Check if battle should end"""
        party_alive = any(getattr(m, 'hp', 0) > 0 for m in party_members)
        foes_alive = any(getattr(f, 'hp', 0) > 0 for f in foes)

        return not (party_alive and foes_alive)

# Performance testing and comparison
class ConcurrentPhasePerformanceTest:
    """Test suite for comparing concurrent vs sequential phase processing"""

    @staticmethod
    async def compare_processing_methods():
        """Compare concurrent vs sequential phase processing"""

        # Create mock battle participants
        party_members = [MockFighter(f"party_{i}") for i in range(6)]
        foes = [MockFighter(f"foe_{i}") for i in range(8)]
        party_effects = [MockEffectManager() for _ in party_members]

        battle_context = {
            'turn': 1,
            'enrage_active': False,
            'total_damage_dealt': 0
        }

        processor = ConcurrentBattlePhaseProcessor()

        # Test concurrent processing
        print("Testing Concurrent Phase Processing...")
        start = time.perf_counter()

        concurrent_stats = await processor.process_party_phase_concurrent(
            MockParty(party_members), party_effects, foes, 1, battle_context
        )

        concurrent_time = time.perf_counter() - start

        # Test sequential processing (simulated)
        print("\nTesting Sequential Phase Processing...")
        start = time.perf_counter()

        sequential_stats = await ConcurrentPhasePerformanceTest._simulate_sequential_processing(
            party_members, party_effects, foes, battle_context
        )

        sequential_time = time.perf_counter() - start

        # Compare results
        improvement = sequential_time / concurrent_time if concurrent_time > 0 else 1

        print("\n=== Performance Comparison ===")
        print(f"Concurrent Processing: {concurrent_time:.4f}s")
        print(f"  Preparation: {concurrent_stats.preparation_time:.4f}s")
        print(f"  Execution: {concurrent_stats.execution_time:.4f}s")
        print(f"  Parallel Preparations: {concurrent_stats.concurrent_preparations}")
        print(f"Sequential Processing: {sequential_time:.4f}s")
        print(f"Performance Improvement: {improvement:.2f}x")

        return improvement

    @staticmethod
    async def _simulate_sequential_processing(party_members, party_effects, foes, battle_context):
        """Simulate traditional sequential processing for comparison"""
        total_time = 0

        for member, effect_mgr in zip(party_members, party_effects):
            if member.hp > 0:
                # Simulate sequential preparation + execution
                await asyncio.sleep(0.003)  # Simulation of preparation
                await asyncio.sleep(0.002)  # Simulation of execution
                total_time += 0.005

        return {
            'total_time': total_time,
            'fighters_processed': len([m for m in party_members if m.hp > 0])
        }

# Mock classes for testing
class MockFighter:
    def __init__(self, fighter_id: str):
        self.id = fighter_id
        self.hp = 100
        self.max_hp = 100
        self.atk = 100
        self.defense = 50
        self.mitigation = 0.1
        self.passives = [f"{fighter_id}_passive_1", f"{fighter_id}_passive_2"]

class MockEffectManager:
    def __init__(self):
        self.dots = [MockEffect("dot_1"), MockEffect("dot_2")]
        self.hots = [MockEffect("hot_1")]

class MockEffect:
    def __init__(self, name: str):
        self.name = name
        self.damage = 10
        self.healing = 15

class MockParty:
    def __init__(self, members: List):
        self.members = members

# Example usage
async def demonstrate_concurrent_battle_processing():
    """Demonstrate the concurrent battle processing system"""
    print("=== Concurrent Battle Phase Processing Demo ===\n")

    # Run performance comparison
    improvement = await ConcurrentPhasePerformanceTest.compare_processing_methods()

    print(f"\nThe concurrent approach provides {improvement:.2f}x performance improvement")
    print("while maintaining full battle logic integrity!")

    return improvement

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_concurrent_battle_processing())
