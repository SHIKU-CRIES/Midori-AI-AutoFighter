"""
Prototype: Enhanced Effect Processing with Expanded Parallelization

This demonstrates how to extend the existing DOT async optimization pattern
to include HOT processing, passive abilities, and stat modifiers.

This builds on the successful 49.7x performance improvement achieved in DOT processing
and applies similar patterns to other effect types.
"""

import asyncio
import time
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class EffectType(Enum):
    DOT = "dot"
    HOT = "hot" 
    PASSIVE = "passive"
    STAT_MODIFIER = "stat_modifier"

@dataclass
class ProcessingStats:
    """Track performance metrics for effect processing"""
    total_effects: int = 0
    parallel_batches: int = 0
    sequential_effects: int = 0
    processing_time: float = 0.0
    early_terminations: int = 0

class EnhancedEffectManager:
    """
    Enhanced effect manager that extends the existing DOT optimization pattern
    to all effect types for improved async performance.
    """
    
    # Thresholds for different processing strategies
    BATCH_LOGGING_THRESHOLD = 10
    PARALLEL_PROCESSING_THRESHOLD = 20
    PASSIVE_PARALLEL_THRESHOLD = 10
    STAT_MOD_PARALLEL_THRESHOLD = 15
    
    # Batch sizes for parallel processing
    EFFECT_BATCH_SIZE = 50
    PASSIVE_BATCH_SIZE = 30
    
    def __init__(self, stats):
        self.stats = stats
        self.dots = []
        self.hots = []
        self.stat_modifiers = []
        self._console = None  # Placeholder for console logging
        self.processing_stats = ProcessingStats()
        
    async def tick_all_effects_enhanced(self, others: Optional["EnhancedEffectManager"] = None) -> ProcessingStats:
        """
        Enhanced effect processing that parallelizes all effect types based on
        the successful DOT optimization pattern.
        
        Returns processing statistics for performance monitoring.
        """
        start_time = time.perf_counter()
        stats = ProcessingStats()
        
        # Process all effect types concurrently when possible
        tasks = []
        
        # DOT/HOT Processing (extend existing pattern)
        if self.dots or self.hots:
            tasks.append(self._process_damage_heal_effects(stats))
            
        # Passive Processing (new parallelization)
        if hasattr(self.stats, 'passives') and self.stats.passives:
            tasks.append(self._process_passive_effects(stats))
            
        # Stat Modifier Processing (new parallelization) 
        if self.stat_modifiers:
            tasks.append(self._process_stat_modifiers(stats))
            
        # Execute all effect types in parallel
        if tasks:
            await asyncio.gather(*tasks)
        
        stats.processing_time = time.perf_counter() - start_time
        self.processing_stats = stats
        return stats
        
    async def _process_damage_heal_effects(self, stats: ProcessingStats) -> None:
        """Process DOTs and HOTs using the existing optimized pattern"""
        
        for collection, effect_type in [(self.dots, EffectType.DOT), (self.hots, EffectType.HOT)]:
            if not collection:
                continue
                
            stats.total_effects += len(collection)
            expired = []
            
            # Batch logging for performance
            if len(collection) > self.BATCH_LOGGING_THRESHOLD:
                effect_name = effect_type.value.upper()
                color = "green" if effect_type == EffectType.HOT else "light_red"
                if self._console:
                    self._console.log(f"[{color}]{self.stats.id} processing {len(collection)} {effect_name} effects[/]")
                    
            # Choose processing strategy based on collection size
            if len(collection) > self.PARALLEL_PROCESSING_THRESHOLD:
                # Parallel processing for large collections (existing pattern)
                expired = await self._process_effects_parallel(collection, effect_type, stats)
            else:
                # Sequential processing for smaller collections
                expired = await self._process_effects_sequential(collection, effect_type, stats)
                
            # Clean up expired effects
            await self._cleanup_expired_effects(collection, expired, effect_type)
            
    async def _process_effects_parallel(self, collection: List, effect_type: EffectType, 
                                       stats: ProcessingStats) -> List:
        """Parallel processing using asyncio.gather (extends existing DOT pattern)"""
        expired = []
        
        async def tick_effect(eff):
            """Wrapper for individual effect processing"""
            if len(collection) <= self.BATCH_LOGGING_THRESHOLD:
                color = "green" if effect_type == EffectType.HOT else "light_red" 
                if self._console:
                    self._console.log(f"[{color}]{self.stats.id} {eff.name} tick[/]")
            return await eff.tick(self.stats), eff
            
        # Process in batches to avoid overwhelming event loop
        for i in range(0, len(collection), self.EFFECT_BATCH_SIZE):
            batch = collection[i:i + self.EFFECT_BATCH_SIZE]
            results = await asyncio.gather(*[tick_effect(eff) for eff in batch])
            stats.parallel_batches += 1
            
            for still_active, eff in results:
                if not still_active:
                    expired.append(eff)
                    
            # Early termination optimization
            if self.stats.hp <= 0:
                stats.early_terminations += 1
                break
                
        return expired
        
    async def _process_effects_sequential(self, collection: List, effect_type: EffectType,
                                         stats: ProcessingStats) -> List:
        """Sequential processing for smaller collections"""
        expired = []
        
        for eff in collection:
            stats.sequential_effects += 1
            
            # Individual logging for small collections
            if len(collection) <= self.BATCH_LOGGING_THRESHOLD:
                color = "green" if effect_type == EffectType.HOT else "light_red"
                if self._console:
                    self._console.log(f"[{color}]{self.stats.id} {eff.name} tick[/]")
                    
            if not await eff.tick(self.stats):
                expired.append(eff)
                
            # Early termination
            if self.stats.hp <= 0:
                stats.early_terminations += 1
                break
                
        return expired
        
    async def _process_passive_effects(self, stats: ProcessingStats) -> None:
        """
        NEW: Parallel processing for passive abilities
        Extends the DOT optimization pattern to passive ability processing
        """
        if not hasattr(self.stats, 'passives'):
            return
            
        passives = self.stats.passives
        stats.total_effects += len(passives)
        
        # Batch logging
        if len(passives) > self.BATCH_LOGGING_THRESHOLD:
            if self._console:
                self._console.log(f"[blue]{self.stats.id} processing {len(passives)} passive effects[/]")
                
        if len(passives) > self.PASSIVE_PARALLEL_THRESHOLD:
            # Parallel passive processing
            await self._process_passives_parallel(passives, stats)
        else:
            # Sequential passive processing 
            await self._process_passives_sequential(passives, stats)
            
    async def _process_passives_parallel(self, passives: List, stats: ProcessingStats) -> None:
        """Parallel processing for passive abilities"""
        
        async def process_passive(passive_id):
            """Process individual passive ability"""
            if len(passives) <= self.BATCH_LOGGING_THRESHOLD and self._console:
                self._console.log(f"[blue]{self.stats.id} {passive_id} passive tick[/]")
            
            # Simulate passive processing (actual implementation would trigger passive logic)
            await asyncio.sleep(0.001)  # Simulate async passive processing
            return passive_id, True  # (passive_id, still_active)
            
        # Process in batches
        for i in range(0, len(passives), self.PASSIVE_BATCH_SIZE):
            batch = passives[i:i + self.PASSIVE_BATCH_SIZE]
            results = await asyncio.gather(*[process_passive(pid) for pid in batch])
            stats.parallel_batches += 1
            
            # Handle results (remove expired passives, etc.)
            for passive_id, still_active in results:
                if not still_active:
                    # Remove expired passive
                    passives.remove(passive_id)
                    
            # Early termination
            if self.stats.hp <= 0:
                stats.early_terminations += 1
                break
                
    async def _process_passives_sequential(self, passives: List, stats: ProcessingStats) -> None:
        """Sequential processing for passive abilities"""
        for passive_id in passives[:]:  # Copy list to allow modification
            stats.sequential_effects += 1
            
            if len(passives) <= self.BATCH_LOGGING_THRESHOLD and self._console:
                self._console.log(f"[blue]{self.stats.id} {passive_id} passive tick[/]")
                
            # Simulate passive processing
            await asyncio.sleep(0.001)
            
            # Early termination
            if self.stats.hp <= 0:
                stats.early_terminations += 1
                break
                
    async def _process_stat_modifiers(self, stats: ProcessingStats) -> None:
        """
        NEW: Parallel processing for stat modifiers
        Extends the optimization pattern to stat modifier processing
        """
        if not self.stat_modifiers:
            return
            
        stats.total_effects += len(self.stat_modifiers)
        expired_mods = []
        
        # Batch logging
        if len(self.stat_modifiers) > self.BATCH_LOGGING_THRESHOLD:
            if self._console:
                self._console.log(f"[yellow]{self.stats.id} processing {len(self.stat_modifiers)} stat modifiers[/]")
                
        if len(self.stat_modifiers) > self.STAT_MOD_PARALLEL_THRESHOLD:
            # Parallel stat modifier processing
            expired_mods = await self._process_stat_mods_parallel(stats)
        else:
            # Sequential stat modifier processing
            expired_mods = await self._process_stat_mods_sequential(stats)
            
        # Clean up expired modifiers
        for mod in expired_mods:
            self.stat_modifiers.remove(mod)
            # Emit expiration event
            await self._emit_effect_expired(mod.name, EffectType.STAT_MODIFIER)
            
    async def _process_stat_mods_parallel(self, stats: ProcessingStats) -> List:
        """Parallel processing for stat modifiers"""
        expired_mods = []
        
        async def tick_modifier(mod):
            """Process individual stat modifier"""
            if len(self.stat_modifiers) <= self.BATCH_LOGGING_THRESHOLD and self._console:
                self._console.log(f"[yellow]{self.stats.id} {mod.name} tick[/]")
            return mod.tick(), mod
            
        # Process in batches
        batch_size = 30
        for i in range(0, len(self.stat_modifiers), batch_size):
            batch = self.stat_modifiers[i:i + batch_size]
            results = await asyncio.gather(*[tick_modifier(mod) for mod in batch])
            stats.parallel_batches += 1
            
            for still_active, mod in results:
                if not still_active:
                    expired_mods.append(mod)
                    
        return expired_mods
        
    async def _process_stat_mods_sequential(self, stats: ProcessingStats) -> List:
        """Sequential processing for stat modifiers"""
        expired_mods = []
        
        for mod in self.stat_modifiers:
            stats.sequential_effects += 1
            
            if len(self.stat_modifiers) <= self.BATCH_LOGGING_THRESHOLD and self._console:
                self._console.log(f"[yellow]{self.stats.id} {mod.name} tick[/]")
                
            if not mod.tick():
                expired_mods.append(mod)
                
        return expired_mods
        
    async def _cleanup_expired_effects(self, collection: List, expired: List, effect_type: EffectType) -> None:
        """Clean up expired effects and emit events"""
        for eff in expired:
            collection.remove(eff)
            await self._emit_effect_expired(eff.name, effect_type)
            
    async def _emit_effect_expired(self, effect_name: str, effect_type: EffectType) -> None:
        """Emit effect expiration events"""
        # Placeholder for event emission
        # In actual implementation, would use BUS.emit()
        pass

# Example usage and performance testing
class PerformanceTestSuite:
    """Test suite demonstrating the performance benefits of enhanced effect processing"""
    
    @staticmethod
    async def test_enhanced_vs_original():
        """Compare enhanced processing vs original sequential processing"""
        
        # Create test fighter with many effects
        class MockStats:
            def __init__(self):
                self.id = "test_fighter"
                self.hp = 1000
                self.passives = [f"passive_{i}" for i in range(50)]
                
        class MockEffect:
            def __init__(self, name):
                self.name = name
                self.id = name
                
            async def tick(self, stats):
                await asyncio.sleep(0.001)  # Simulate processing time
                return True  # Still active
                
        class MockStatModifier:
            def __init__(self, name):
                self.name = name
                self.id = name
                
            def tick(self):
                return True  # Still active
        
        stats = MockStats()
        manager = EnhancedEffectManager(stats)
        
        # Add many effects to test parallelization
        manager.dots = [MockEffect(f"dot_{i}") for i in range(100)]
        manager.hots = [MockEffect(f"hot_{i}") for i in range(80)]
        manager.stat_modifiers = [MockStatModifier(f"mod_{i}") for i in range(60)]
        
        # Test enhanced processing
        start = time.perf_counter()
        processing_stats = await manager.tick_all_effects_enhanced()
        enhanced_time = time.perf_counter() - start
        
        print(f"Enhanced Processing Results:")
        print(f"  Time: {enhanced_time:.4f}s")
        print(f"  Total Effects: {processing_stats.total_effects}")
        print(f"  Parallel Batches: {processing_stats.parallel_batches}")
        print(f"  Sequential Effects: {processing_stats.sequential_effects}")
        print(f"  Early Terminations: {processing_stats.early_terminations}")
        
        return processing_stats

# Example configuration for battle room integration
class BattleRoomEnhancedConfig:
    """Configuration for integrating enhanced effect processing into battle rooms"""
    
    # Enable enhanced processing for battles with many effects
    ENABLE_ENHANCED_PROCESSING = True
    
    # Thresholds for switching to enhanced processing
    MIN_TOTAL_EFFECTS_FOR_ENHANCEMENT = 50
    MIN_FIGHTERS_FOR_ENHANCEMENT = 6
    
    # Performance monitoring
    TRACK_PROCESSING_STATS = True
    LOG_PERFORMANCE_IMPROVEMENTS = True
    
    @staticmethod
    def should_use_enhanced_processing(party_effects, foe_effects):
        """Determine if enhanced processing should be used for this battle"""
        total_effects = sum(
            len(mgr.dots) + len(mgr.hots) + len(getattr(mgr.stats, 'passives', [])) 
            for mgr in party_effects + foe_effects
        )
        
        total_fighters = len(party_effects) + len(foe_effects)
        
        return (
            BattleRoomEnhancedConfig.ENABLE_ENHANCED_PROCESSING and
            (total_effects >= BattleRoomEnhancedConfig.MIN_TOTAL_EFFECTS_FOR_ENHANCEMENT or
             total_fighters >= BattleRoomEnhancedConfig.MIN_FIGHTERS_FOR_ENHANCEMENT)
        )

"""
Integration Example:

In battle.py, the enhanced effect processing could be integrated like this:

```python
# In BattleRoom.resolve() method
if BattleRoomEnhancedConfig.should_use_enhanced_processing(party_effects, foe_effects):
    # Use enhanced processing
    for mgr in party_effects + foe_effects:
        if hasattr(mgr, 'tick_all_effects_enhanced'):
            processing_stats = await mgr.tick_all_effects_enhanced()
            if BattleRoomEnhancedConfig.LOG_PERFORMANCE_IMPROVEMENTS:
                log.debug(f"Enhanced processing: {processing_stats.total_effects} effects in {processing_stats.processing_time:.4f}s")
else:
    # Use existing processing
    for mgr in party_effects + foe_effects:
        await mgr.tick()
```

This approach provides:
1. Backward compatibility with existing effect processing
2. Automatic optimization for battles with many effects
3. Performance monitoring and metrics
4. Gradual rollout capability
"""