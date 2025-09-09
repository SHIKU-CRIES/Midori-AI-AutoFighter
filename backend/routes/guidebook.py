from __future__ import annotations

from typing import Any

from quart import Blueprint
from quart import jsonify

from autofighter.passives import discover as discover_passives
from autofighter.rooms.shop import PRICE_BY_STARS
from autofighter.rooms.shop import REROLL_COST
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type

bp = Blueprint("guidebook", __name__, url_prefix="/guidebook")


@bp.get("/damage-types")
async def damage_types() -> tuple[str, int, dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    # Enhanced descriptions for each damage type
    enhanced_descriptions = {
        "Fire": "Damage increases based on missing health. Burns enemies with damage-over-time effects. Weak to Ice.",
        "Ice": "Applies Frozen Wound stacks that reduce enemy actions and cause missed turns. Weak to Lightning.",
        "Lightning": "Strikes multiple targets and applies random elemental DoTs. Ultimate adds Aftertaste effect. Weak to Wind.",
        "Wind": "Hits spread to all enemies after first target. Applies Gale Erosion DoT. Ultimate pulls and detonates enemy DoTs. Weak to Fire.",
        "Light": "Provides healing and regeneration to allies. Direct healing for low-HP allies instead of attacking. Weak to Dark.",
        "Dark": "Applies Shadow Siphon to party members, draining HP to boost own attack and defense. Strong single-target damage. Weak to Light."
    }

    for name in ALL_DAMAGE_TYPES:
        inst = load_damage_type(name)
        cls = type(inst)
        desc = enhanced_descriptions.get(name, getattr(cls, "__doc__", None))
        if not desc:
            # Provide a concise fallback description
            weakness = getattr(inst, "weakness", None)
            tail = f" Weak to {weakness}." if weakness else ""
            desc = f"Elemental damage type.{tail}"

        # Calculate what this type is strong against
        strong_against = None
        for other_name in ALL_DAMAGE_TYPES:
            other_inst = load_damage_type(other_name)
            if getattr(other_inst, "weakness", None) == name:
                strong_against = other_name
                break

        entries.append(
            {
                "id": getattr(inst, "id", name),
                "weakness": getattr(inst, "weakness", None),
                "strong_against": strong_against,
                "color": getattr(inst, "color", None),
                "description": str(desc).strip(),
                "damage_mod_weak": "1.25x damage when attacking weakness",
                "damage_mod_resist": "0.75x damage when attacking same type"
            }
        )
    return jsonify({"damage_types": entries}), 200


@bp.get("/ultimates")
async def ultimates() -> tuple[str, int, dict[str, Any]]:
    info: list[dict[str, Any]] = []
    for name in ALL_DAMAGE_TYPES:
        inst = load_damage_type(name)
        cls = type(inst)
        # Try to extract docstring from ultimate implementation
        doc = getattr(cls.ultimate, "__doc__", None)  # type: ignore[attr-defined]
        if not doc:
            # Provide specific fallbacks for known types
            lowers = name.lower()
            if lowers == "lightning":
                doc = "AoE strike; applies random elemental DoTs; adds Aftertaste on hit."
            elif lowers == "light":
                doc = "Heal allies based on missing HP; reduce enemy defenses briefly."
            elif lowers == "dark":
                doc = "Multi-hit dark barrage scaling with DoT stacks; strong single-target damage."
            elif lowers == "wind":
                doc = "Rapid multi-hit across enemies; spreads on-hit interactions."
            elif lowers == "fire":
                doc = "AoE damage and inflict burns; gains temporary drain stacks on use."
            elif lowers == "ice":
                doc = "Strike all foes six times, increasing damage per target."
            else:
                doc = f"{name} ultimate ability."
        info.append({"id": getattr(inst, "id", name), "description": str(doc).strip()})
    return jsonify({"ultimates": info}), 200


@bp.get("/passives")
async def passives() -> tuple[str, int, dict[str, Any]]:
    registry = discover_passives()
    items: list[dict[str, Any]] = []

    # Enhanced descriptions for common passives
    enhanced_descriptions = {
        "room_heal": "Heal for 1 HP at the end of each battle. Each stack provides additional healing.",
        "attack_up": "Gain +5 attack at the start of each battle. Each stack provides additional attack bonus.",
        "ally_overload": "Ally's unique passive that builds up power over multiple turns for devastating attacks.",
        "advanced_combat_synergy": "Provides synergy bonuses when using specific ability combinations.",
        "becca_menagerie_bond": "Becca's unique passive that strengthens bonds with summoned creatures.",
        "bubbles_bubble_burst": "Bubbles' unique passive that creates protective bubble effects.",
        "carly_guardians_aegis": "Carly's unique passive that provides protective aegis effects for the party.",
        "graygray_counter_maestro": "Graygray's unique passive that excels at counter-attacking enemies.",
        "hilander_critical_ferment": "Hilander's unique passive that builds up critical hit potential over time.",
        "ixia_tiny_titan": "Ixia's unique passive that provides increasing power despite small stature.",
        "kboshi_flux_cycle": "Kboshi's unique passive that cycles through different elemental flux states.",
        "lady_darkness_eclipsing_veil": "Lady Darkness's unique passive that shrouds the battlefield in shadow.",
        "lady_echo_resonant_static": "Lady Echo's unique passive that creates resonant static effects.",
        "lady_fire_and_ice_duality_engine": "Lady Fire and Ice's unique passive that balances opposing elements.",
        "lady_light_radiant_aegis": "Lady Light's unique passive that provides radiant protection."
    }

    for pid, cls in sorted(registry.items()):
        name = getattr(cls, "name", pid)
        trigger = getattr(cls, "trigger", None)

        # Use enhanced description if available, otherwise try class docstring
        desc = enhanced_descriptions.get(pid, getattr(cls, "__doc__", ""))
        if not desc:
            # Create a basic description based on the passive name
            if "passive" in name.lower():
                desc = "Unique character ability that provides special effects."
            else:
                desc = f"Passive ability: {name}. Triggers on {trigger or 'specific conditions'}."

        # Get additional metadata if available
        amount = getattr(cls, "amount", None)
        stack_display = getattr(cls, "stack_display", None)

        effect_info = ""
        if amount is not None:
            effect_info += f" Base effect: {amount}"
        if stack_display:
            effect_info += f" (Stacks: {stack_display})"

        items.append(
            {
                "id": pid,
                "name": name,
                "trigger": trigger,
                "description": str(desc).strip() + effect_info,
                "amount": amount,
                "stack_display": stack_display
            }
        )
    return jsonify({"passives": items}), 200


@bp.get("/shops")
async def shops() -> tuple[str, int, dict[str, Any]]:
    return jsonify({
        "reroll_cost": REROLL_COST,
        "price_by_stars": PRICE_BY_STARS,
        "notes": [
            "Shop stock includes cards and relics; prices scale with rarity (star rating).",
            "Reroll generates a new stock list at a fixed gold cost.",
            "Higher star items are more powerful but significantly more expensive.",
            "Stock quality and quantity may improve as you progress through runs."
        ],
        "pricing_explanation": {
            "1_star": f"{PRICE_BY_STARS.get(1, 10)} gold - Common items, basic effects",
            "2_star": f"{PRICE_BY_STARS.get(2, 25)} gold - Improved effects and utility",
            "3_star": f"{PRICE_BY_STARS.get(3, 50)} gold - Strong effects, good value",
            "4_star": f"{PRICE_BY_STARS.get(4, 100)} gold - Very powerful, rare items",
            "5_star": f"{PRICE_BY_STARS.get(5, 200)} gold - Extremely rare, game-changing",
            "6_star": f"{PRICE_BY_STARS.get(6, 500)} gold - Legendary items, run-defining"
        },
        "strategy_tips": [
            "Save gold early for high-star items that appear later",
            "Reroll when current stock doesn't fit your build",
            "4+ star items can dramatically change your strategy"
        ]
    }), 200


@bp.get("/ui")
async def ui() -> tuple[str, int, dict[str, Any]]:
    tips = [
        {"name": "Overlays", "description": "Open Settings, Inventory, and Guidebook from the main menu."},
        {"name": "Battle Review", "description": "After battles, view damage by type and proceed to the next room."},
        {"name": "Rewards", "description": "Choose cards, relics, and loot when available before advancing."},
    ]
    return jsonify({"tips": tips}), 200


@bp.get("/mechs")
async def mechs() -> tuple[str, int, dict[str, Any]]:
    mechanics = [
        {"name": "Ultimate Charge", "description": "Gain charge during combat; spend it to use your damage type's ultimate."},
        {"name": "DoTs & HoTs", "description": "Damage/Healing over time effects stack and interact with some elements."},
        {"name": "Enrage", "description": "Foes may gain enrage increasing difficulty as rooms progress."},
        {"name": "Elemental Resistances", "description": "Each damage type has a weakness: Fire→Ice, Ice→Lightning, Lightning→Wind, Wind→Fire, Light↔Dark."},
        {"name": "Vitality Scaling", "description": "Healing scales with both healer and target vitality. DoTs use vitality for damage calculations."},
        {"name": "Level Benefits", "description": "Global level increases base stats: +10 max HP, +5 attack, +3 defense per level."},
    ]
    return jsonify({"mechanics": mechanics}), 200


@bp.get("/stats")
async def stats() -> tuple[str, int, dict[str, Any]]:
    """Detailed breakdown of all character stats and their effects."""
    stats_info = [
        {
            "name": "Health Points (HP)",
            "description": "Your current health. When it reaches 0, you're defeated. Can be healed through various means.",
            "base_value": "1000",
            "scaling": "+10 per level"
        },
        {
            "name": "Attack (ATK)",
            "description": "Determines damage dealt to enemies. Higher attack means stronger abilities and ultimates.",
            "base_value": "200",
            "scaling": "+5 per level"
        },
        {
            "name": "Defense (DEF)",
            "description": "Reduces incoming damage. Higher defense makes you more resilient to enemy attacks.",
            "base_value": "200",
            "scaling": "+3 per level"
        },
        {
            "name": "Critical Rate",
            "description": "Chance to deal critical hits for increased damage. Default critical damage is 2x normal damage.",
            "base_value": "5%",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Critical Damage",
            "description": "Multiplier for critical hit damage. Works with critical rate to boost damage output.",
            "base_value": "200%",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Vitality",
            "description": "Multiplier for healing effects. Both healer and target vitality affect healing: healing × healer_vitality × target_vitality.",
            "base_value": "1.0x",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Effect Hit Rate",
            "description": "Chance for your damage-over-time effects and debuffs to successfully apply to enemies.",
            "base_value": "100%",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Effect Resistance",
            "description": "Reduces the chance of enemy effects (DoTs, debuffs) successfully affecting you.",
            "base_value": "5%",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Dodge Rate",
            "description": "Chance to completely avoid incoming attacks, taking no damage.",
            "base_value": "5%",
            "scaling": "Affected by cards and relics"
        },
        {
            "name": "Mitigation",
            "description": "Additional damage reduction multiplier applied after defense calculations.",
            "base_value": "1.0x",
            "scaling": "Affected by cards and relics"
        }
    ]

    # Add passive explanations
    common_passives = [
        {
            "name": "Room Heal",
            "description": "Heal for 1 HP at the end of each battle. Stacks provide additional healing.",
            "trigger": "After battle"
        },
        {
            "name": "Attack Up",
            "description": "Gain +5 attack at the start of each battle. Stacks provide additional attack.",
            "trigger": "Before battle"
        }
    ]

    return jsonify({
        "stats": stats_info,
        "common_passives": common_passives,
        "level_info": {
            "description": "Your global level increases all base stats and unlocks new content.",
            "benefits": "Each level grants: +10 max HP, +5 attack, +3 defense",
            "experience": "Gain XP by winning battles and completing runs"
        }
    }), 200
