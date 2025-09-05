# Rank Badge Plan

Fighter portraits now accept an optional `rankTag` property reserved for future badge rendering. The component currently ignores the tag until a design is finalized.

## Badge Tiers
- Bronze `#cd7f32`
- Silver `#c0c0c0`
- Gold `#ffd700`
- Platinum `#e5e4e2`
- Diamond `#b9f2ff`

## Backend Rank Mapping
| Backend Rank   | Badge Tier | Notes |
|---------------|------------|-------|
| `normal`      | Bronze     | |
| `prime`       | Silver     | |
| `boss`        | Platinum   | |
| `glitched prime` | Gold     | Glitchy outline effect |
| `glitched boss`  | Diamond  | Glitchy outline effect |

## Badge Style
- Small circular badge overlay anchored to a portrait corner.
- Star icons for Bronze through Gold.
- Laurel wreath for Platinum.
- Diamond glyph for Diamond tier.
- Subtle drop shadow to distinguish from the portrait.
- Glitched ranks reuse the same tier color but add a jittering, glitchy outline.

These guidelines outline future UI work for rank badges.
