# Combat Viewer

The Combat Viewer provides detailed real-time combat monitoring and enhanced battle logging capabilities during active battles.

## Overview

The Combat Viewer allows players to inspect detailed combat information during battles, including character stats, status effects, and battle performance metrics. The system automatically pauses combat when opened to allow thorough inspection without missing critical information.

## Access

The Combat Viewer is accessible through an Eye icon button in the top-left navbar, which is visible only during active battles.

## Interface Layout

The Combat Viewer features a three-panel layout:

### Left Panel - Character List
- Shows all characters in the battle
- **Party Members**: Listed first with green highlighting
- **Foes**: Listed below party members
- Displays character name and current HP for quick reference
- Click any character to view their detailed information

### Center Panel - Character Details
When a character is selected, the center panel displays:

#### Health Information
- Current HP / Maximum HP
- Shield values (if applicable)

#### Combat Stats
- Attack, Defense, Crit Rate, Mitigation
- Effect Hit Rate, Effect Resistance
- Action Points (AP) and Actions Per Turn (APT)

#### Battle Performance
- Damage Dealt
- Damage Taken  
- Kills (number of enemies defeated)
- Healing Done (if applicable)

#### Element Type
- Character's damage type/element (Fire, Ice, Light, Dark, etc.)

### Right Panel - Status Effects
The right panel contains a tabbed interface for viewing different types of status effects:

#### DoTs (Damage over Time)
- Effect name and damage per turn
- Remaining duration
- Total potential damage calculation
- Element type and source information

#### HoTs (Healing over Time)  
- Effect name and healing per turn
- Remaining duration
- Total potential healing calculation
- Element type and source information

#### Buffs
- Positive status effects
- Duration and description
- Source (from passives, relics, cards, etc.)

#### Debuffs
- Negative status effects
- Duration and description
- Source information

#### Relics
- Currently active relics
- Star rating and full description
- Permanent effects explanation

#### Cards
- Active card effects
- Star rating and stat modifications
- Detailed descriptions of bonuses

#### Passives
- Character passive abilities
- Permanent or temporary passive effects
- Detailed ability descriptions

## Enhanced Status Effect Information

Each status effect displays comprehensive information:

- **Effect Name and Type**: Clear identification
- **Duration**: Remaining turns or permanent status
- **Damage/Healing Values**: Per-turn amounts and total potential
- **Source Information**: Whether from relics, cards, passives, or temporary effects
- **Element Information**: Associated element type
- **Comprehensive Details**: Description and calculated impact

## Battle Pause/Resume System

### Automatic Pause
- Combat automatically pauses when the Combat Viewer is opened
- Ensures no important information is missed during inspection
- "Combat paused" message appears in the console

### Seamless Resume
- Combat automatically resumes when the Combat Viewer is closed
- No manual intervention required
- Battle continues from where it was paused

## Usage Example

During a battle:

1. **Open**: Click the Eye icon in the navbar to open the Combat Viewer
2. **Inspect**: Select any character to view their detailed stats and status effects
3. **Navigate**: Browse through different effect types using the tabbed interface
4. **Analyze**: Review comprehensive information about each effect's impact and duration
5. **Close**: Click the × button or close the viewer to resume combat automatically

## Technical Implementation

### Frontend Components
- **CombatViewer.svelte**: Main three-panel interface component
- **NavBar Integration**: Eye icon button with proper event handling
- **Real-time Data**: Integrates with existing battle snapshot polling

### Backend API Enhancements  
- **Catalog Endpoints**: `/catalog/relics`, `/catalog/cards`, `/catalog/dots`, `/catalog/hots`
- **Enhanced Descriptions**: Detailed information for all effect types
- **Pause/Resume API**: Battle state control through `/rooms/<run_id>/battle` endpoints

### Data Flow
1. Battle snapshots provide real-time character and effect data
2. Catalog API provides detailed descriptions for effects
3. Pause/resume calls modify battle task state without interrupting data flow
4. Enhanced logging captures all combat events for detailed analysis

## Benefits

- **Detailed Analysis**: Comprehensive view of all combat effects and their impact
- **Strategic Planning**: Understanding of current battle state and effect timing
- **Learning Tool**: Helps players understand game mechanics and effect interactions
- **Performance Tracking**: Real-time battle performance metrics
- **No Missed Information**: Automatic pause ensures nothing important is overlooked

The Combat Viewer enhances the strategic depth of the game by providing players with complete visibility into combat mechanics while maintaining the game's responsive design patterns.