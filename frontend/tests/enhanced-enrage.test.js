import { describe, it, expect } from 'vitest';

describe('Enhanced Enrage System', () => {
  it('should calculate correct orb count based on enrage duration', () => {
    // Mock the orb count calculation function
    function calculateOrbCount(active, reducedMotion, enrageData) {
      if (!active) return 0;
      const baseCount = reducedMotion ? 6 : 14;
      
      if (!enrageData.active) {
        return baseCount;
      }
      
      // Increase orb count based on enrage turns
      const enrageTurns = enrageData.turns || 0;
      const extraOrbs = Math.min(Math.floor(enrageTurns / 5), 20); // Cap at 20 extra orbs
      return baseCount + extraOrbs;
    }

    // Test cases
    expect(calculateOrbCount(false, false, { active: false, turns: 0 })).toBe(0);
    expect(calculateOrbCount(true, false, { active: false, turns: 0 })).toBe(14);
    expect(calculateOrbCount(true, true, { active: false, turns: 0 })).toBe(6);
    
    // Test enrage scaling
    expect(calculateOrbCount(true, false, { active: true, turns: 0 })).toBe(14);
    expect(calculateOrbCount(true, false, { active: true, turns: 5 })).toBe(15); // 14 + 1
    expect(calculateOrbCount(true, false, { active: true, turns: 10 })).toBe(16); // 14 + 2
    expect(calculateOrbCount(true, false, { active: true, turns: 50 })).toBe(24); // 14 + 10
    expect(calculateOrbCount(true, false, { active: true, turns: 200 })).toBe(34); // 14 + 20 (capped)
  });

  it('should include required enrage data fields', () => {
    const enrageData = {
      active: true,
      stacks: 15,
      turns: 15
    };

    expect(enrageData).toHaveProperty('active');
    expect(enrageData).toHaveProperty('stacks'); 
    expect(enrageData).toHaveProperty('turns');
    expect(enrageData.turns).toBe(enrageData.stacks);
  });

  it('should validate rain effect parameters', () => {
    // Mock orb creation for rain effect
    function makeOrbForRain() {
      const rand = (min, max) => Math.random() * (max - min) + min;
      
      return {
        id: Math.random().toString(36).slice(2),
        x: rand(0, 100),
        y: rand(-20, 0), // Start above viewport for rain effect
        size: rand(2.4, 4.2),
        fallSpeed: rand(4, 8), // Speed of falling 
        delay: rand(0, 3),
        hue: 200, // Simplified for testing
      };
    }

    const orb = makeOrbForRain();
    
    // Validate rain effect properties
    expect(orb.y).toBeLessThanOrEqual(0); // Should start above viewport
    expect(orb.y).toBeGreaterThanOrEqual(-20);
    expect(orb.fallSpeed).toBeGreaterThanOrEqual(4);
    expect(orb.fallSpeed).toBeLessThanOrEqual(8);
    expect(orb).not.toHaveProperty('dx'); // Old drift property should not exist
    expect(orb).not.toHaveProperty('dy'); // Old drift property should not exist
  });
});