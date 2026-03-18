"""
Pokemon League Champion - Game Data
All Pokemon stats, moves, type charts, and starter configurations.
Abilities, items, natures ported from PokemonBattleEngine (Kermalis).
"""
from enums import (
    MoveCategory, MoveEffect, MoveFlag,
)

# ─── Natures ────────────────────────────────────────────────────────
# Each nature: (boosted_stat, lowered_stat) or None for neutral
NATURES = {
    "Hardy":   None,
    "Lonely":  ("atk", "def"),
    "Brave":   ("atk", "spe"),
    "Adamant": ("atk", "spa"),
    "Naughty": ("atk", "spd"),
    "Bold":    ("def", "atk"),
    "Docile":  None,
    "Relaxed": ("def", "spe"),
    "Impish":  ("def", "spa"),
    "Lax":     ("def", "spd"),
    "Timid":   ("spe", "atk"),
    "Hasty":   ("spe", "def"),
    "Serious": None,
    "Jolly":   ("spe", "spa"),
    "Naive":   ("spe", "spd"),
    "Modest":  ("spa", "atk"),
    "Mild":    ("spa", "def"),
    "Quiet":   ("spa", "spe"),
    "Bashful": None,
    "Rash":    ("spa", "spd"),
    "Calm":    ("spd", "atk"),
    "Gentle":  ("spd", "def"),
    "Sassy":   ("spd", "spe"),
    "Careful": ("spd", "spa"),
    "Quirky":  None,
}

# ─── Abilities ──────────────────────────────────────────────────────
# Ability name -> description dict (logic is in battle_logic.py)
ABILITIES = {
    # Offensive
    "Blaze": "Powers up Fire moves when HP is low.",
    "Torrent": "Powers up Water moves when HP is low.",
    "Overgrow": "Powers up Grass moves when HP is low.",
    "Swarm": "Powers up Bug moves when HP is low.",
    "Guts": "Boosts Attack when statused.",
    "Huge Power": "Doubles Attack.",
    "Pure Power": "Doubles Attack.",
    "Hustle": "Boosts Attack but lowers accuracy.",
    "Iron Fist": "Boosts punching moves.",
    "Reckless": "Boosts recoil moves.",
    "Adaptability": "STAB becomes 2x instead of 1.5x.",
    "Technician": "Boosts weak moves (base power ≤60).",
    "Sniper": "Critical hits do more damage.",
    "Super Luck": "Higher critical hit ratio.",
    "Tinted Lens": "Not-very-effective moves do normal damage.",
    "Speed Boost": "Speed raises each turn.",
    "Moxie": "Attack rises on KO.",
    "Download": "Raises Atk or SpAtk on switch-in based on foe.",
    "Intimidate": "Lowers foe's Attack on switch-in.",
    # Defensive
    "Sturdy": "Survives with 1 HP from full.",
    "Multiscale": "Halves damage at full HP.",
    "Filter": "Reduces super-effective damage.",
    "Solid Rock": "Reduces super-effective damage.",
    "Thick Fat": "Halves Fire and Ice damage taken.",
    "Levitate": "Immune to Ground moves.",
    "Flash Fire": "Fire moves boost own Fire power instead of dealing damage.",
    "Water Absorb": "Heals from Water moves instead of taking damage.",
    "Volt Absorb": "Heals from Electric moves instead of taking damage.",
    "Lightning Rod": "Draws Electric moves and boosts SpAtk.",
    "Storm Drain": "Draws Water moves and boosts SpAtk.",
    "Marvel Scale": "Boosts Defense when statused.",
    "Ice Body": "Heals in Hail.",
    "Rain Dish": "Heals in Rain.",
    "Sand Stream": "Summons Sandstorm on switch-in.",
    "Snow Warning": "Summons Hail on switch-in.",
    "Drought": "Summons Sun on switch-in.",
    "Drizzle": "Summons Rain on switch-in.",
    "Sand Veil": "Evasion up in Sandstorm.",
    "Snow Cloak": "Evasion up in Hail.",
    "Overcoat": "Immune to weather damage.",
    "Battle Armor": "Cannot be crit.",
    "Shell Armor": "Cannot be crit.",
    "Clear Body": "Prevents stat drops by foes.",
    "White Smoke": "Prevents stat drops by foes.",
    "Magic Guard": "Only takes direct attack damage.",
    "Poison Heal": "Heals from poison instead of taking damage.",
    "Natural Cure": "Cures status on switch-out.",
    # Status / Utility
    "Serene Grace": "Doubles secondary effect chances.",
    "Compound Eyes": "Boosts accuracy.",
    "No Guard": "All moves hit.",
    "Prankster": "Status moves get +1 priority.",
    "Immunity": "Immune to poison.",
    "Limber": "Immune to paralysis.",
    "Insomnia": "Immune to sleep.",
    "Vital Spirit": "Immune to sleep.",
    "Magma Armor": "Immune to freeze.",
    "Water Veil": "Immune to burn.",
    "Own Tempo": "Immune to confusion.",
    "Oblivious": "Immune to infatuation.",
    "Inner Focus": "Immune to flinch.",
    "Shed Skin": "Chance to cure status each turn.",
    "Pressure": "Foe uses extra PP.",
    "Unaware": "Ignores stat changes.",
    "Contrary": "Stat changes are reversed.",
    "Simple": "Stat changes are doubled.",
    "Skill Link": "Multi-hit moves always hit 5 times.",
    "Rock Head": "No recoil damage.",
    "Defeatist": "Halves offensive stats below 50% HP.",
    "Slow Start": "Halves Attack and Speed for 5 turns.",
    "Truant": "Can only attack every other turn.",
    "Color Change": "Type changes to the type of last hit received.",
    "Rough Skin": "Damages attacker on contact.",
    "Iron Barbs": "Damages attacker on contact.",
    "Flame Body": "May burn on contact.",
    "Static": "May paralyze on contact.",
    "Poison Point": "May poison on contact.",
    "Cute Charm": "May infatuate on contact.",
    "Effect Spore": "May inflict status on contact.",
    "Mold Breaker": "Ignores target's ability.",
    "Teravolt": "Ignores target's ability.",
    "Turboblaze": "Ignores target's ability.",
    "Regenerator": "Heals 1/3 HP on switch-out.",
    "Sand Force": "Boosts Rock/Ground/Steel in Sandstorm.",
}

# ─── Items ──────────────────────────────────────────────────────────
ITEMS = {
    # Choice items
    "Choice Band": "Boosts Attack 1.5x but locks move.",
    "Choice Specs": "Boosts SpAtk 1.5x but locks move.",
    "Choice Scarf": "Boosts Speed 1.5x but locks move.",
    # Life Orb
    "Life Orb": "Boosts damage 1.3x but lose 10% HP each attack.",
    # Type boosters (1.2x)
    "Charcoal": "Boosts Fire moves 1.2x.",
    "Mystic Water": "Boosts Water moves 1.2x.",
    "Miracle Seed": "Boosts Grass moves 1.2x.",
    "Magnet": "Boosts Electric moves 1.2x.",
    "Never-Melt Ice": "Boosts Ice moves 1.2x.",
    "Black Belt": "Boosts Fighting moves 1.2x.",
    "Poison Barb": "Boosts Poison moves 1.2x.",
    "Soft Sand": "Boosts Ground moves 1.2x.",
    "Sharp Beak": "Boosts Flying moves 1.2x.",
    "Twisted Spoon": "Boosts Psychic moves 1.2x.",
    "Silver Powder": "Boosts Bug moves 1.2x.",
    "Hard Stone": "Boosts Rock moves 1.2x.",
    "Spell Tag": "Boosts Ghost moves 1.2x.",
    "Dragon Fang": "Boosts Dragon moves 1.2x.",
    "Black Glasses": "Boosts Dark moves 1.2x.",
    "Metal Coat": "Boosts Steel moves 1.2x.",
    "Silk Scarf": "Boosts Normal moves 1.2x.",
    # Category boosters
    "Muscle Band": "Boosts physical moves 1.1x.",
    "Wise Glasses": "Boosts special moves 1.1x.",
    # Defensive
    "Leftovers": "Restores 1/16 HP each turn.",
    "Black Sludge": "Restores 1/16 HP if Poison, damages otherwise.",
    "Eviolite": "Boosts Def/SpDef 1.5x for not-fully-evolved.",
    "Assault Vest": "Boosts SpDef 1.5x but can only use attacks.",
    "Focus Sash": "Survives with 1 HP from full (consumed).",
    "Rocky Helmet": "Damages attacker 1/6 on contact.",
    # Expert Belt
    "Expert Belt": "Super-effective moves do 1.2x.",
    # Berries
    "Sitrus Berry": "Restores 25% HP when below 50%.",
    "Lum Berry": "Cures any status (consumed).",
    # Mega Stones / Z-Crystals not applicable, keeping it gen5-style
    "None": "No item.",
}

# Type -> item that boosts it 1.2x
TYPE_BOOSTING_ITEMS = {
    "Fire": "Charcoal",
    "Water": "Mystic Water",
    "Grass": "Miracle Seed",
    "Electric": "Magnet",
    "Ice": "Never-Melt Ice",
    "Fighting": "Black Belt",
    "Poison": "Poison Barb",
    "Ground": "Soft Sand",
    "Flying": "Sharp Beak",
    "Psychic": "Twisted Spoon",
    "Bug": "Silver Powder",
    "Rock": "Hard Stone",
    "Ghost": "Spell Tag",
    "Dragon": "Dragon Fang",
    "Dark": "Black Glasses",
    "Steel": "Metal Coat",
    "Normal": "Silk Scarf",
    "Fairy": "Silk Scarf",  # No official fairy item in gen5
}

# Reverse lookup: item name -> type it boosts
ITEM_TYPE_BOOST = {v: k for k, v in TYPE_BOOSTING_ITEMS.items()}

# ─── Type Effectiveness Chart ───────────────────────────────────────
# Maps (attacking_type, defending_type) -> multiplier
# Only super-effective (2.0) and not-very-effective (0.5) and immune (0.0) listed.
# Anything not listed is neutral (1.0).

TYPE_CHART = {
    ("Fire", "Grass"): 2.0,
    ("Fire", "Ice"): 2.0,
    ("Fire", "Bug"): 2.0,
    ("Fire", "Steel"): 2.0,
    ("Fire", "Water"): 0.5,
    ("Fire", "Rock"): 0.5,
    ("Fire", "Fire"): 0.5,
    ("Fire", "Dragon"): 0.5,
    ("Water", "Fire"): 2.0,
    ("Water", "Ground"): 2.0,
    ("Water", "Rock"): 2.0,
    ("Water", "Water"): 0.5,
    ("Water", "Grass"): 0.5,
    ("Water", "Dragon"): 0.5,
    ("Grass", "Water"): 2.0,
    ("Grass", "Ground"): 2.0,
    ("Grass", "Rock"): 2.0,
    ("Grass", "Grass"): 0.5,
    ("Grass", "Fire"): 0.5,
    ("Grass", "Poison"): 0.5,
    ("Grass", "Flying"): 0.5,
    ("Grass", "Bug"): 0.5,
    ("Grass", "Dragon"): 0.5,
    ("Grass", "Steel"): 0.5,
    ("Electric", "Water"): 2.0,
    ("Electric", "Flying"): 2.0,
    ("Electric", "Electric"): 0.5,
    ("Electric", "Grass"): 0.5,
    ("Electric", "Dragon"): 0.5,
    ("Electric", "Ground"): 0.0,
    ("Ice", "Grass"): 2.0,
    ("Ice", "Ground"): 2.0,
    ("Ice", "Flying"): 2.0,
    ("Ice", "Dragon"): 2.0,
    ("Ice", "Fire"): 0.5,
    ("Ice", "Water"): 0.5,
    ("Ice", "Ice"): 0.5,
    ("Ice", "Steel"): 0.5,
    ("Fighting", "Normal"): 2.0,
    ("Fighting", "Ice"): 2.0,
    ("Fighting", "Rock"): 2.0,
    ("Fighting", "Dark"): 2.0,
    ("Fighting", "Steel"): 2.0,
    ("Fighting", "Poison"): 0.5,
    ("Fighting", "Flying"): 0.5,
    ("Fighting", "Psychic"): 0.5,
    ("Fighting", "Bug"): 0.5,
    ("Fighting", "Fairy"): 0.5,
    ("Fighting", "Ghost"): 0.0,
    ("Poison", "Grass"): 2.0,
    ("Poison", "Fairy"): 2.0,
    ("Poison", "Poison"): 0.5,
    ("Poison", "Ground"): 0.5,
    ("Poison", "Rock"): 0.5,
    ("Poison", "Ghost"): 0.5,
    ("Poison", "Steel"): 0.0,
    ("Ground", "Fire"): 2.0,
    ("Ground", "Electric"): 2.0,
    ("Ground", "Poison"): 2.0,
    ("Ground", "Rock"): 2.0,
    ("Ground", "Steel"): 2.0,
    ("Ground", "Grass"): 0.5,
    ("Ground", "Bug"): 0.5,
    ("Ground", "Flying"): 0.0,
    ("Flying", "Grass"): 2.0,
    ("Flying", "Fighting"): 2.0,
    ("Flying", "Bug"): 2.0,
    ("Flying", "Electric"): 0.5,
    ("Flying", "Rock"): 0.5,
    ("Flying", "Steel"): 0.5,
    ("Psychic", "Fighting"): 2.0,
    ("Psychic", "Poison"): 2.0,
    ("Psychic", "Psychic"): 0.5,
    ("Psychic", "Steel"): 0.5,
    ("Psychic", "Dark"): 0.0,
    ("Bug", "Grass"): 2.0,
    ("Bug", "Psychic"): 2.0,
    ("Bug", "Dark"): 2.0,
    ("Bug", "Fire"): 0.5,
    ("Bug", "Fighting"): 0.5,
    ("Bug", "Poison"): 0.5,
    ("Bug", "Flying"): 0.5,
    ("Bug", "Ghost"): 0.5,
    ("Bug", "Steel"): 0.5,
    ("Bug", "Fairy"): 0.5,
    ("Rock", "Fire"): 2.0,
    ("Rock", "Ice"): 2.0,
    ("Rock", "Flying"): 2.0,
    ("Rock", "Bug"): 2.0,
    ("Rock", "Fighting"): 0.5,
    ("Rock", "Ground"): 0.5,
    ("Rock", "Steel"): 0.5,
    ("Ghost", "Psychic"): 2.0,
    ("Ghost", "Ghost"): 2.0,
    ("Ghost", "Dark"): 0.5,
    ("Ghost", "Normal"): 0.0,
    ("Dragon", "Dragon"): 2.0,
    ("Dragon", "Steel"): 0.5,
    ("Dragon", "Fairy"): 0.0,
    ("Dark", "Psychic"): 2.0,
    ("Dark", "Ghost"): 2.0,
    ("Dark", "Fighting"): 0.5,
    ("Dark", "Dark"): 0.5,
    ("Dark", "Fairy"): 0.5,
    ("Steel", "Ice"): 2.0,
    ("Steel", "Rock"): 2.0,
    ("Steel", "Fairy"): 2.0,
    ("Steel", "Fire"): 0.5,
    ("Steel", "Water"): 0.5,
    ("Steel", "Electric"): 0.5,
    ("Steel", "Steel"): 0.5,
    ("Fairy", "Fighting"): 2.0,
    ("Fairy", "Dragon"): 2.0,
    ("Fairy", "Dark"): 2.0,
    ("Fairy", "Fire"): 0.5,
    ("Fairy", "Poison"): 0.5,
    ("Fairy", "Steel"): 0.5,
    ("Normal", "Rock"): 0.5,
    ("Normal", "Steel"): 0.5,
    ("Normal", "Ghost"): 0.0,
}


def get_type_multiplier(atk_type, def_types):
    """Get combined type effectiveness multiplier."""
    mult = 1.0
    for dt in def_types:
        mult *= TYPE_CHART.get((atk_type, dt), 1.0)
    return mult


# ─── Move Data ──────────────────────────────────────────────────────
# Each move: {type, category, power, accuracy, effect, effect_chance, flags, priority, recoil_divisor}
# Defaults: effect=HIT, effect_chance=0, flags=NONE, priority=0

_C = MoveFlag.MAKES_CONTACT
_HC = MoveFlag.HIGH_CRIT
_DF = MoveFlag.DEFROST_USER
_P = MoveFlag.PUNCHING

MOVES_DB = {
    # ── Normal ──
    "Tackle":       {"type": "Normal", "category": "physical", "power": 40, "accuracy": 100, "flags": _C},
    "Quick Attack": {"type": "Normal", "category": "physical", "power": 40, "accuracy": 100, "flags": _C, "priority": 1},
    "Body Slam":    {"type": "Normal", "category": "physical", "power": 85, "accuracy": 100, "flags": _C, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 30},
    "Hyper Beam":   {"type": "Normal", "category": "special",  "power": 150, "accuracy": 90},
    "Slash":        {"type": "Normal", "category": "physical", "power": 70, "accuracy": 100, "flags": _C | _HC},
    "Facade":       {"type": "Normal", "category": "physical", "power": 70, "accuracy": 100, "flags": _C, "effect": MoveEffect.FACADE},
    "Return":       {"type": "Normal", "category": "physical", "power": 102, "accuracy": 100, "flags": _C},
    "Extreme Speed":{"type": "Normal", "category": "physical", "power": 80, "accuracy": 100, "flags": _C, "priority": 2},
    "Explosion":    {"type": "Normal", "category": "physical", "power": 250, "accuracy": 100, "effect": MoveEffect.SELF_DESTRUCT},
    "Rapid Spin":   {"type": "Normal", "category": "physical", "power": 20, "accuracy": 100, "flags": _C, "effect": MoveEffect.RAPID_SPIN},
    "Protect":      {"type": "Normal", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.PROTECT, "priority": 4},
    # ── Fire ──
    "Ember":        {"type": "Fire", "category": "special",  "power": 40, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 10},
    "Flamethrower": {"type": "Fire", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 10},
    "Fire Blast":   {"type": "Fire", "category": "special",  "power": 110, "accuracy": 85, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 30},
    "Fire Punch":   {"type": "Fire", "category": "physical", "power": 75, "accuracy": 100, "flags": _C | _P, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 10},
    "Blaze Kick":   {"type": "Fire", "category": "physical", "power": 85, "accuracy": 90, "flags": _C | _HC, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 10},
    "Flare Blitz":  {"type": "Fire", "category": "physical", "power": 120, "accuracy": 100, "flags": _C | _DF, "effect": MoveEffect.RECOIL, "recoil_divisor": 3, "effect_chance": 10},
    "Will-O-Wisp":  {"type": "Fire", "category": "status",   "power": 0, "accuracy": 85, "effect": MoveEffect.BURN},
    "Sunny Day":    {"type": "Fire", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.SUNNY_DAY},
    "Eruption":     {"type": "Fire", "category": "special",  "power": 150, "accuracy": 100, "effect": MoveEffect.ERUPTION},
    # ── Water ──
    "Water Gun":    {"type": "Water", "category": "special",  "power": 40, "accuracy": 100},
    "Surf":         {"type": "Water", "category": "special",  "power": 90, "accuracy": 100},
    "Hydro Pump":   {"type": "Water", "category": "special",  "power": 110, "accuracy": 80},
    "Aqua Tail":    {"type": "Water", "category": "physical", "power": 90, "accuracy": 90, "flags": _C},
    "Waterfall":    {"type": "Water", "category": "physical", "power": 80, "accuracy": 100, "flags": _C, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 20},
    "Scald":        {"type": "Water", "category": "special",  "power": 80, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 30},
    "Aqua Jet":     {"type": "Water", "category": "physical", "power": 40, "accuracy": 100, "flags": _C, "priority": 1},
    "Rain Dance":   {"type": "Water", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.RAIN_DANCE},
    # ── Grass ──
    "Vine Whip":    {"type": "Grass", "category": "physical", "power": 45, "accuracy": 100, "flags": _C},
    "Razor Leaf":   {"type": "Grass", "category": "physical", "power": 55, "accuracy": 95, "flags": _HC},
    "Solar Beam":   {"type": "Grass", "category": "special",  "power": 120, "accuracy": 100},
    "Energy Ball":  {"type": "Grass", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 10},
    "Leaf Blade":   {"type": "Grass", "category": "physical", "power": 90, "accuracy": 100, "flags": _C | _HC},
    "Giga Drain":   {"type": "Grass", "category": "special",  "power": 75, "accuracy": 100, "effect": MoveEffect.HP_DRAIN},
    "Leech Seed":   {"type": "Grass", "category": "status",   "power": 0, "accuracy": 90, "effect": MoveEffect.LEECH_SEED_EFFECT},
    "Spore":        {"type": "Grass", "category": "status",   "power": 0, "accuracy": 100, "effect": MoveEffect.SLEEP},
    "Synthesis":    {"type": "Grass", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.HEAL},
    # ── Electric ──
    "Thunder Shock":{"type": "Electric", "category": "special",  "power": 40, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 10},
    "Thunderbolt":  {"type": "Electric", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 10},
    "Thunder":      {"type": "Electric", "category": "special",  "power": 110, "accuracy": 70, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 30},
    "Spark":        {"type": "Electric", "category": "physical", "power": 65, "accuracy": 100, "flags": _C, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 30},
    "Wild Charge":  {"type": "Electric", "category": "physical", "power": 90, "accuracy": 100, "flags": _C, "effect": MoveEffect.RECOIL, "recoil_divisor": 4},
    "Volt Switch":  {"type": "Electric", "category": "special",  "power": 70, "accuracy": 100},
    "Thunder Wave": {"type": "Electric", "category": "status",   "power": 0, "accuracy": 90, "effect": MoveEffect.PARALYZE},
    # ── Ice ──
    "Ice Shard":    {"type": "Ice", "category": "physical", "power": 40, "accuracy": 100, "priority": 1},
    "Ice Beam":     {"type": "Ice", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_FREEZE, "effect_chance": 10},
    "Blizzard":     {"type": "Ice", "category": "special",  "power": 110, "accuracy": 70, "effect": MoveEffect.HIT_MAYBE_FREEZE, "effect_chance": 10},
    "Ice Punch":    {"type": "Ice", "category": "physical", "power": 75, "accuracy": 100, "flags": _C | _P, "effect": MoveEffect.HIT_MAYBE_FREEZE, "effect_chance": 10},
    "Hail":         {"type": "Ice", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.HAIL},
    # ── Fighting ──
    "Karate Chop":  {"type": "Fighting", "category": "physical", "power": 50, "accuracy": 100, "flags": _C | _HC},
    "Close Combat": {"type": "Fighting", "category": "physical", "power": 120, "accuracy": 100, "flags": _C},
    "Aura Sphere":  {"type": "Fighting", "category": "special",  "power": 80, "accuracy": 0},  # Never misses
    "Brick Break":  {"type": "Fighting", "category": "physical", "power": 75, "accuracy": 100, "flags": _C},
    "Mach Punch":   {"type": "Fighting", "category": "physical", "power": 40, "accuracy": 100, "flags": _C | _P, "priority": 1},
    "Drain Punch":  {"type": "Fighting", "category": "physical", "power": 75, "accuracy": 100, "flags": _C | _P, "effect": MoveEffect.HP_DRAIN},
    "Superpower":   {"type": "Fighting", "category": "physical", "power": 120, "accuracy": 100, "flags": _C},
    "Focus Blast":  {"type": "Fighting", "category": "special",  "power": 120, "accuracy": 70, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 10},
    # ── Poison ──
    "Poison Sting": {"type": "Poison", "category": "physical", "power": 15, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_POISON, "effect_chance": 30},
    "Sludge Bomb":  {"type": "Poison", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_POISON, "effect_chance": 30},
    "Cross Poison": {"type": "Poison", "category": "physical", "power": 70, "accuracy": 100, "flags": _C | _HC, "effect": MoveEffect.HIT_MAYBE_POISON, "effect_chance": 10},
    "Toxic":        {"type": "Poison", "category": "status",   "power": 0, "accuracy": 90, "effect": MoveEffect.TOXIC},
    "Toxic Spikes": {"type": "Poison", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.TOXIC_SPIKES_EFFECT},
    "Venoshock":    {"type": "Poison", "category": "special",  "power": 65, "accuracy": 100, "effect": MoveEffect.VENOSHOCK},
    # ── Ground ──
    "Mud Slap":     {"type": "Ground", "category": "special",  "power": 20, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_ACC, "effect_chance": 100},
    "Earthquake":   {"type": "Ground", "category": "physical", "power": 100, "accuracy": 100},
    "Dig":          {"type": "Ground", "category": "physical", "power": 80, "accuracy": 100, "flags": _C},
    "Earth Power":  {"type": "Ground", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 10},
    # ── Flying ──
    "Gust":         {"type": "Flying", "category": "special",  "power": 40, "accuracy": 100},
    "Air Slash":    {"type": "Flying", "category": "special",  "power": 75, "accuracy": 95, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 30},
    "Brave Bird":   {"type": "Flying", "category": "physical", "power": 120, "accuracy": 100, "flags": _C, "effect": MoveEffect.RECOIL, "recoil_divisor": 3},
    "Aerial Ace":   {"type": "Flying", "category": "physical", "power": 60, "accuracy": 0, "flags": _C},  # Never misses
    "Roost":        {"type": "Flying", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.HEAL},
    # ── Psychic ──
    "Confusion":    {"type": "Psychic", "category": "special",  "power": 50, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_CONFUSE, "effect_chance": 10},
    "Psychic":      {"type": "Psychic", "category": "special",  "power": 90, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 10},
    "Psyshock":     {"type": "Psychic", "category": "special",  "power": 80, "accuracy": 100, "effect": MoveEffect.PSYSHOCK_EFFECT},
    "Zen Headbutt": {"type": "Psychic", "category": "physical", "power": 80, "accuracy": 90, "flags": _C, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 20},
    "Calm Mind":    {"type": "Psychic", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.CHANGE_TARGET_SPATK, "effect_param": 1},
    "Trick Room":   {"type": "Psychic", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.TRICK_ROOM_EFFECT, "priority": -7},
    "Reflect":      {"type": "Psychic", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.REFLECT_EFFECT},
    "Light Screen": {"type": "Psychic", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.LIGHT_SCREEN_EFFECT},
    # ── Bug ──
    "Bug Bite":     {"type": "Bug", "category": "physical", "power": 60, "accuracy": 100, "flags": _C},
    "X-Scissor":    {"type": "Bug", "category": "physical", "power": 80, "accuracy": 100, "flags": _C},
    "Signal Beam":  {"type": "Bug", "category": "special",  "power": 75, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_CONFUSE, "effect_chance": 10},
    "U-Turn":       {"type": "Bug", "category": "physical", "power": 70, "accuracy": 100, "flags": _C},
    # ── Rock ──
    "Rock Throw":   {"type": "Rock", "category": "physical", "power": 50, "accuracy": 90},
    "Rock Slide":   {"type": "Rock", "category": "physical", "power": 75, "accuracy": 90, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 30},
    "Stone Edge":   {"type": "Rock", "category": "physical", "power": 100, "accuracy": 80, "flags": _HC},
    "Stealth Rock": {"type": "Rock", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.STEALTH_ROCK_EFFECT},
    # ── Ghost ──
    "Shadow Ball":  {"type": "Ghost", "category": "special",  "power": 80, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 20},
    "Shadow Claw":  {"type": "Ghost", "category": "physical", "power": 70, "accuracy": 100, "flags": _C | _HC},
    "Hex":          {"type": "Ghost", "category": "special",  "power": 65, "accuracy": 100, "effect": MoveEffect.HEX_EFFECT},
    "Shadow Sneak": {"type": "Ghost", "category": "physical", "power": 40, "accuracy": 100, "flags": _C, "priority": 1},
    # ── Dragon ──
    "Dragon Claw":  {"type": "Dragon", "category": "physical", "power": 80, "accuracy": 100, "flags": _C},
    "Dragon Pulse": {"type": "Dragon", "category": "special",  "power": 85, "accuracy": 100},
    "Outrage":      {"type": "Dragon", "category": "physical", "power": 120, "accuracy": 100, "flags": _C},
    "Draco Meteor": {"type": "Dragon", "category": "special",  "power": 130, "accuracy": 90},
    "Dragon Dance": {"type": "Dragon", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.CHANGE_TARGET_ATK, "effect_param": 1},
    # ── Dark ──
    "Bite":         {"type": "Dark", "category": "physical", "power": 60, "accuracy": 100, "flags": _C | MoveFlag.BITING, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 30},
    "Crunch":       {"type": "Dark", "category": "physical", "power": 80, "accuracy": 100, "flags": _C | MoveFlag.BITING, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_DEF, "effect_chance": 20},
    "Dark Pulse":   {"type": "Dark", "category": "special",  "power": 80, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 20},
    "Sucker Punch": {"type": "Dark", "category": "physical", "power": 70, "accuracy": 100, "flags": _C, "priority": 1},
    "Knock Off":    {"type": "Dark", "category": "physical", "power": 65, "accuracy": 100, "flags": _C},
    "Pursuit":      {"type": "Dark", "category": "physical", "power": 40, "accuracy": 100, "flags": _C},
    "Swords Dance": {"type": "Normal", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.CHANGE_TARGET_ATK, "effect_param": 2},
    "Nasty Plot":   {"type": "Dark", "category": "status",    "power": 0, "accuracy": 0, "effect": MoveEffect.CHANGE_TARGET_SPATK, "effect_param": 2},
    # ── Steel ──
    "Iron Tail":    {"type": "Steel", "category": "physical", "power": 100, "accuracy": 75, "flags": _C, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_DEF, "effect_chance": 30},
    "Flash Cannon": {"type": "Steel", "category": "special",  "power": 80, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF, "effect_chance": 10},
    "Metal Claw":   {"type": "Steel", "category": "physical", "power": 50, "accuracy": 95, "flags": _C, "effect": MoveEffect.HIT_MAYBE_RAISE_USER_ATK, "effect_chance": 10},
    "Bullet Punch": {"type": "Steel", "category": "physical", "power": 40, "accuracy": 100, "flags": _C | _P, "priority": 1},
    "Iron Head":    {"type": "Steel", "category": "physical", "power": 80, "accuracy": 100, "flags": _C, "effect": MoveEffect.HIT_MAYBE_FLINCH, "effect_chance": 30},
    # ── Fairy ──
    "Fairy Wind":   {"type": "Fairy", "category": "special",  "power": 40, "accuracy": 100},
    "Moonblast":    {"type": "Fairy", "category": "special",  "power": 95, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_SPATK, "effect_chance": 30},
    "Dazzling Gleam":{"type": "Fairy", "category": "special", "power": 80, "accuracy": 100},
    "Play Rough":   {"type": "Fairy", "category": "physical", "power": 90, "accuracy": 90, "flags": _C, "effect": MoveEffect.HIT_MAYBE_LOWER_TARGET_DEF, "effect_chance": 10},
    # ── Additional ──
    "Fire Fang":    {"type": "Fire", "category": "physical", "power": 65, "accuracy": 95, "flags": _C | MoveFlag.BITING, "effect": MoveEffect.HIT_MAYBE_BURN, "effect_chance": 10},
    "Dragon Breath":{"type": "Dragon", "category": "special",  "power": 60, "accuracy": 100, "effect": MoveEffect.HIT_MAYBE_PARALYZE, "effect_chance": 30},
    "Wing Attack":  {"type": "Flying", "category": "physical", "power": 60, "accuracy": 100, "flags": _C},
    "Power Gem":    {"type": "Rock", "category": "special",  "power": 80, "accuracy": 100},
    # ── Status moves ──
    "Toxic":        {"type": "Poison", "category": "status", "power": 0, "accuracy": 90, "effect": MoveEffect.TOXIC},
    "Spikes":       {"type": "Ground", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.SPIKES_EFFECT},
    "Recover":      {"type": "Normal", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.HEAL},
    "Wish":         {"type": "Normal", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.HEAL},
    "Taunt":        {"type": "Dark", "category": "status",   "power": 0, "accuracy": 100},
    "Substitute":   {"type": "Normal", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.SUBSTITUTE_EFFECT},
    "Focus Energy": {"type": "Normal", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.FOCUS_ENERGY},
    "Rest":         {"type": "Psychic", "category": "status", "power": 0, "accuracy": 0, "effect": MoveEffect.REST},
    "Tailwind":     {"type": "Flying", "category": "status",  "power": 0, "accuracy": 0, "effect": MoveEffect.TAILWIND_EFFECT},
    "Haze":         {"type": "Ice", "category": "status",     "power": 0, "accuracy": 0, "effect": MoveEffect.HAZE},
    "Belly Drum":   {"type": "Normal", "category": "status",  "power": 0, "accuracy": 0, "effect": MoveEffect.BELLY_DRUM},
    "Shell Smash":  {"type": "Normal", "category": "status",  "power": 0, "accuracy": 0, "effect": MoveEffect.CHANGE_TARGET_ATK, "effect_param": 2},
    "Curse":        {"type": "Ghost", "category": "status",   "power": 0, "accuracy": 0, "effect": MoveEffect.CURSE},
    "Confuse Ray":  {"type": "Ghost", "category": "status",   "power": 0, "accuracy": 100, "effect": MoveEffect.CONFUSE},
    # ── Auto-added ──
    "Seed Bomb": {"type": "Grass", "category": "physical", "power": 80, "accuracy": 100},
    # ── Auto-added ──
    "Take Down": {"type": "Normal", "category": "physical", "power": 90, "accuracy": 85},
    # ── Auto-added ──
    "Power Whip": {"type": "Grass", "category": "physical", "power": 120, "accuracy": 85},
    # ── Auto-added ──
    "Petal Dance": {"type": "Grass", "category": "special", "power": 120, "accuracy": 100},
    # ── Auto-added ──
    "Petal Blizzard": {"type": "Grass", "category": "physical", "power": 90, "accuracy": 100},
    # ── Auto-added ──
    "Scratch": {"type": "Normal", "category": "physical", "power": 40, "accuracy": 100},
    # ── Auto-added ──
    "Fire Spin": {"type": "Fire", "category": "special", "power": 35, "accuracy": 85},
    # ── Auto-added ──
    "Inferno": {"type": "Fire", "category": "special", "power": 100, "accuracy": 50},
    # ── Auto-added ──
    "Heat Wave": {"type": "Fire", "category": "special", "power": 95, "accuracy": 90},
    # ── Auto-added ──
    "Water Pulse": {"type": "Water", "category": "special", "power": 60, "accuracy": 100},
    # ── Auto-added ──
    "Wave Crash": {"type": "Water", "category": "physical", "power": 120, "accuracy": 100},
    # ── Auto-added ──
    "Psybeam": {"type": "Psychic", "category": "special", "power": 65, "accuracy": 100},
    # ── Auto-added ──
    "Bug Buzz": {"type": "Bug", "category": "special", "power": 90, "accuracy": 100},
    # ── Auto-added ──
    "Pin Missile": {"type": "Bug", "category": "physical", "power": 15, "accuracy": 100},
    # ── Auto-added ──
    "Brutal Swing": {"type": "Dark", "category": "physical", "power": 60, "accuracy": 100},
    # ── Auto-added ──
    "Lunge": {"type": "Bug", "category": "physical", "power": 80, "accuracy": 100},
    # ── Auto-added ──
    "Poison Jab": {"type": "Poison", "category": "physical", "power": 80, "accuracy": 100},
    # ── Auto-added ──
    "Drill Run": {"type": "Ground", "category": "physical", "power": 80, "accuracy": 100},
    # ── Auto-added ──
    "Twister": {"type": "Dragon", "category": "special", "power": 40, "accuracy": 100},
    # ── Auto-added ──
    "Hurricane": {"type": "Flying", "category": "special", "power": 110, "accuracy": 100},
}


# ─── Pokemon Data ───────────────────────────────────────────────────
# base_hp, base_atk, base_def, base_spa, base_spd, base_spe
# move_tiers: dict of {move_type: [tier1_move, tier2_move, ...]} (weakest to strongest)

POKEMON_DB = {
    # ══════════ Fire ══════════
    "Charmander": {
        "types": ["Fire"],
        "stats": {"hp": 39, "atk": 52, "def": 43, "spa": 60, "spd": 50, "spe": 65},
        "abilities": ["Blaze"],
        "move_tiers": {"Normal": ["Scratch", "Slash"], "Fire": ["Fire Spin", "Ember", "Fire Fang", "Flamethrower", "Inferno", "Flare Blitz"], "Dragon": ["Dragon Breath"]},
    },
    "Growlithe": {
        "types": ["Fire"],
        "stats": {"hp": 55, "atk": 70, "def": 45, "spa": 70, "spd": 50, "spe": 60},
        "abilities": ["Intimidate", "Flash Fire"],
        "move_tiers": {"Fire": ["Ember", "Fire Fang", "Flare Blitz"], "Normal": ["Tackle", "Body Slam"]},
    },
    "Charmeleon": {
        "types": ["Fire"],
        "stats": {"hp": 58, "atk": 64, "def": 58, "spa": 80, "spd": 65, "spe": 80},
        "abilities": ["Blaze"],
        "move_tiers": {"Normal": ["Scratch", "Slash"], "Fire": ["Ember", "Fire Fang", "Flamethrower", "Inferno", "Flare Blitz"], "Dragon": ["Dragon Breath"]},
    },
    "Flareon": {
        "types": ["Fire"],
        "stats": {"hp": 65, "atk": 130, "def": 60, "spa": 95, "spd": 110, "spe": 65},
        "abilities": ["Flash Fire"],
        "move_tiers": {"Fire": ["Ember", "Fire Fang", "Flare Blitz"], "Normal": ["Quick Attack", "Body Slam", "Return"]},
    },
    "Arcanine": {
        "types": ["Fire"],
        "stats": {"hp": 90, "atk": 110, "def": 80, "spa": 100, "spd": 80, "spe": 95},
        "abilities": ["Intimidate", "Flash Fire"],
        "move_tiers": {"Fire": ["Ember", "Flamethrower", "Flare Blitz"], "Normal": ["Body Slam", "Extreme Speed"], "Dark": ["Crunch"]},
    },
    "Charizard": {
        "types": ["Fire", "Flying"],
        "stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
        "abilities": ["Blaze", "Drought"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Claw"], "Fire": ["Fire Spin", "Ember", "Fire Fang", "Flamethrower", "Heat Wave", "Inferno", "Flare Blitz"], "Normal": ["Scratch", "Slash"], "Flying": ["Air Slash"]},
    },
    "Blaziken": {
        "types": ["Fire", "Fighting"],
        "stats": {"hp": 80, "atk": 120, "def": 70, "spa": 110, "spd": 70, "spe": 80},
        "abilities": ["Blaze", "Speed Boost"],
        "move_tiers": {"Fire": ["Ember", "Blaze Kick", "Flare Blitz"], "Fighting": ["Brick Break", "Close Combat"], "Flying": ["Brave Bird"]},
    },
    "Chandelure": {
        "types": ["Ghost", "Fire"],
        "stats": {"hp": 60, "atk": 55, "def": 90, "spa": 145, "spd": 90, "spe": 80},
        "abilities": ["Flash Fire", "Flame Body"],
        "move_tiers": {"Fire": ["Ember", "Flamethrower", "Fire Blast"], "Ghost": ["Hex", "Shadow Ball"], "Dark": ["Dark Pulse"]},
    },
    "Magmortar": {
        "types": ["Fire"],
        "stats": {"hp": 75, "atk": 95, "def": 67, "spa": 125, "spd": 95, "spe": 83},
        "abilities": ["Flame Body"],
        "move_tiers": {"Fire": ["Ember", "Flamethrower", "Fire Blast"], "Psychic": ["Psychic"], "Electric": ["Thunderbolt"]},
    },
    # ══════════ Water ══════════
    "Squirtle": {
        "types": ["Water"],
        "stats": {"hp": 44, "atk": 48, "def": 65, "spa": 50, "spd": 64, "spe": 43},
        "abilities": ["Torrent", "Rain Dish"],
        "move_tiers": {"Normal": ["Tackle", "Rapid Spin"], "Water": ["Water Gun", "Water Pulse", "Aqua Tail", "Hydro Pump", "Wave Crash"], "Dark": ["Bite"]},
    },
    "Wartortle": {
        "types": ["Water"],
        "stats": {"hp": 59, "atk": 63, "def": 80, "spa": 65, "spd": 80, "spe": 58},
        "abilities": ["Torrent", "Rain Dish"],
        "move_tiers": {"Normal": ["Tackle", "Rapid Spin"], "Water": ["Water Gun", "Water Pulse", "Aqua Tail", "Hydro Pump", "Wave Crash"], "Dark": ["Bite"]},
    },
    "Vaporeon": {
        "types": ["Water"],
        "stats": {"hp": 130, "atk": 65, "def": 60, "spa": 110, "spd": 95, "spe": 65},
        "abilities": ["Water Absorb"],
        "move_tiers": {"Water": ["Water Gun", "Surf", "Hydro Pump"], "Ice": ["Ice Beam"], "Normal": ["Body Slam"]},
    },
    "Blastoise": {
        "types": ["Water"],
        "stats": {"hp": 79, "atk": 83, "def": 100, "spa": 85, "spd": 105, "spe": 78},
        "abilities": ["Torrent", "Rain Dish"],
        "move_tiers": {"Normal": ["Tackle", "Rapid Spin"], "Water": ["Water Gun", "Water Pulse", "Aqua Tail", "Hydro Pump", "Wave Crash"], "Steel": ["Flash Cannon"], "Dark": ["Bite"]},
    },
    "Starmie": {
        "types": ["Water", "Psychic"],
        "stats": {"hp": 60, "atk": 75, "def": 85, "spa": 100, "spd": 85, "spe": 115},
        "abilities": ["Natural Cure"],
        "move_tiers": {"Water": ["Water Gun", "Surf", "Hydro Pump"], "Psychic": ["Confusion", "Psychic"], "Ice": ["Ice Beam"]},
    },
    "Gyarados": {
        "types": ["Water", "Flying"],
        "stats": {"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81},
        "abilities": ["Intimidate", "Moxie"],
        "move_tiers": {"Water": ["Water Gun", "Waterfall", "Aqua Tail"], "Dark": ["Bite", "Crunch"], "Ground": ["Earthquake"]},
    },
    "Milotic": {
        "types": ["Water"],
        "stats": {"hp": 95, "atk": 60, "def": 79, "spa": 100, "spd": 125, "spe": 81},
        "abilities": ["Marvel Scale", "Competitive"],
        "move_tiers": {"Water": ["Water Gun", "Surf", "Hydro Pump"], "Ice": ["Ice Beam"], "Dragon": ["Dragon Pulse"]},
    },
    "Lapras": {
        "types": ["Water", "Ice"],
        "stats": {"hp": 130, "atk": 85, "def": 80, "spa": 85, "spd": 95, "spe": 60},
        "abilities": ["Water Absorb", "Shell Armor"],
        "move_tiers": {"Water": ["Water Gun", "Surf", "Hydro Pump"], "Ice": ["Ice Shard", "Ice Beam", "Blizzard"], "Electric": ["Thunderbolt"]},
    },
    # ══════════ Grass ══════════
    "Bulbasaur": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "abilities": ["Overgrow"],
        "move_tiers": {"Normal": ["Tackle", "Take Down"], "Grass": ["Vine Whip", "Razor Leaf", "Seed Bomb", "Power Whip", "Solar Beam"]},
    },
    "Roserade": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 60, "atk": 70, "def": 65, "spa": 125, "spd": 105, "spe": 90},
        "abilities": ["Natural Cure", "Poison Point"],
        "move_tiers": {"Grass": ["Giga Drain", "Energy Ball"], "Poison": ["Sludge Bomb"], "Fairy": ["Dazzling Gleam"], "Ghost": ["Shadow Ball"]},
    },
    "Sceptile": {
        "types": ["Grass"],
        "stats": {"hp": 70, "atk": 85, "def": 65, "spa": 105, "spd": 85, "spe": 120},
        "abilities": ["Overgrow"],
        "move_tiers": {"Grass": ["Vine Whip", "Leaf Blade", "Energy Ball"], "Dragon": ["Dragon Claw"], "Normal": ["Quick Attack", "Return"]},
    },
    "Ivysaur": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 60, "atk": 62, "def": 63, "spa": 80, "spd": 80, "spe": 60},
        "abilities": ["Overgrow"],
        "move_tiers": {"Normal": ["Tackle", "Take Down"], "Grass": ["Vine Whip", "Razor Leaf", "Seed Bomb", "Power Whip", "Solar Beam"]},
    },
    "Venusaur": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 80, "atk": 82, "def": 83, "spa": 100, "spd": 100, "spe": 80},
        "abilities": ["Overgrow", "Thick Fat"],
        "move_tiers": {"Grass": ["Vine Whip", "Razor Leaf", "Seed Bomb", "Petal Blizzard", "Petal Dance", "Power Whip", "Solar Beam"], "Normal": ["Tackle", "Take Down"]},
    },


    # ══════════ Electric ══════════
    "Pikachu": {
        "types": ["Electric"],
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "abilities": ["Static", "Lightning Rod"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Thunder"], "Normal": ["Quick Attack", "Slash"]},
    },
    "Raichu": {
        "types": ["Electric"],
        "stats": {"hp": 60, "atk": 90, "def": 55, "spa": 90, "spd": 80, "spe": 110},
        "abilities": ["Static", "Lightning Rod"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Thunder"], "Normal": ["Quick Attack", "Body Slam"], "Fighting": ["Brick Break"]},
    },
    "Jolteon": {
        "types": ["Electric"],
        "stats": {"hp": 65, "atk": 65, "def": 60, "spa": 110, "spd": 95, "spe": 130},
        "abilities": ["Volt Absorb"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Thunder"], "Ghost": ["Shadow Ball"]},
    },
    "Luxray": {
        "types": ["Electric"],
        "stats": {"hp": 80, "atk": 120, "def": 79, "spa": 95, "spd": 79, "spe": 70},
        "abilities": ["Intimidate", "Guts"],
        "move_tiers": {"Electric": ["Spark", "Wild Charge"], "Dark": ["Bite", "Crunch"], "Normal": ["Facade", "Return"]},
    },
    "Ampharos": {
        "types": ["Electric"],
        "stats": {"hp": 90, "atk": 75, "def": 85, "spa": 115, "spd": 90, "spe": 55},
        "abilities": ["Static"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Thunder"], "Dragon": ["Dragon Pulse"], "Fighting": ["Focus Blast"]},
    },
    "Electivire": {
        "types": ["Electric"],
        "stats": {"hp": 75, "atk": 123, "def": 67, "spa": 95, "spd": 85, "spe": 95},
        "abilities": ["Motor Drive"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Wild Charge"], "Fighting": ["Brick Break", "Close Combat"], "Ice": ["Ice Punch"]},
    },
    "Magnezone": {
        "types": ["Electric", "Steel"],
        "stats": {"hp": 70, "atk": 70, "def": 115, "spa": 130, "spd": 90, "spe": 60},
        "abilities": ["Sturdy", "Magnet Pull"],
        "move_tiers": {"Electric": ["Thunder Shock", "Thunderbolt", "Thunder"], "Steel": ["Flash Cannon"], "Normal": ["Body Slam"]},
    },
    # ══════════ Ice ══════════
    "Glaceon": {
        "types": ["Ice"],
        "stats": {"hp": 65, "atk": 60, "def": 110, "spa": 130, "spd": 95, "spe": 65},
        "abilities": ["Snow Cloak", "Ice Body"],
        "move_tiers": {"Ice": ["Ice Shard", "Ice Beam", "Blizzard"], "Ghost": ["Shadow Ball"], "Normal": ["Body Slam"]},
    },
    "Weavile": {
        "types": ["Dark", "Ice"],
        "stats": {"hp": 70, "atk": 120, "def": 65, "spa": 45, "spd": 85, "spe": 125},
        "abilities": ["Pressure"],
        "move_tiers": {"Dark": ["Pursuit", "Knock Off", "Crunch"], "Ice": ["Ice Shard", "Ice Punch"]},
    },
    # ══════════ Fighting ══════════
    "Machamp": {
        "types": ["Fighting"],
        "stats": {"hp": 90, "atk": 130, "def": 80, "spa": 65, "spd": 85, "spe": 55},
        "abilities": ["Guts", "No Guard"],
        "move_tiers": {"Fighting": ["Karate Chop", "Brick Break", "Close Combat"], "Rock": ["Rock Slide"], "Ice": ["Ice Punch"]},
    },
    "Lucario": {
        "types": ["Fighting", "Steel"],
        "stats": {"hp": 70, "atk": 110, "def": 70, "spa": 115, "spd": 70, "spe": 90},
        "abilities": ["Steadfast", "Inner Focus"],
        "move_tiers": {"Fighting": ["Brick Break", "Close Combat"], "Steel": ["Bullet Punch", "Flash Cannon"], "Dark": ["Dark Pulse"]},
    },
    # ══════════ Poison ══════════
    "Gengar": {
        "types": ["Ghost", "Poison"],
        "stats": {"hp": 60, "atk": 65, "def": 60, "spa": 130, "spd": 75, "spe": 110},
        "abilities": ["Levitate"],
        "move_tiers": {"Ghost": ["Hex", "Shadow Ball"], "Poison": ["Sludge Bomb"], "Dark": ["Dark Pulse"], "Electric": ["Thunderbolt"]},
    },
    "Crobat": {
        "types": ["Poison", "Flying"],
        "stats": {"hp": 85, "atk": 90, "def": 80, "spa": 70, "spd": 80, "spe": 130},
        "abilities": ["Inner Focus"],
        "move_tiers": {"Poison": ["Cross Poison", "Sludge Bomb"], "Flying": ["Air Slash", "Brave Bird"], "Dark": ["Bite", "Crunch"]},
    },
    # ══════════ Ground ══════════
    "Sandshrew": {
        "types": ["Ground"],
        "stats": {"hp": 50, "atk": 75, "def": 85, "spa": 20, "spd": 30, "spe": 40},
        "abilities": ["Sand Veil"],
        "move_tiers": {"Ground": ["Mud Slap", "Dig", "Earthquake"], "Normal": ["Slash"], "Rock": ["Rock Slide"]},
    },
    "Sandslash": {
        "types": ["Ground"],
        "stats": {"hp": 75, "atk": 100, "def": 110, "spa": 45, "spd": 55, "spe": 65},
        "abilities": ["Sand Veil"],
        "move_tiers": {"Ground": ["Mud Slap", "Dig", "Earthquake"], "Normal": ["Slash", "Return"], "Rock": ["Rock Slide", "Stone Edge"]},
    },
    "Flygon": {
        "types": ["Ground", "Dragon"],
        "stats": {"hp": 80, "atk": 100, "def": 80, "spa": 80, "spd": 80, "spe": 100},
        "abilities": ["Levitate"],
        "move_tiers": {"Ground": ["Earth Power", "Earthquake"], "Dragon": ["Dragon Claw", "Outrage"], "Rock": ["Rock Slide"]},
    },
    "Hippowdon": {
        "types": ["Ground"],
        "stats": {"hp": 108, "atk": 112, "def": 118, "spa": 68, "spd": 72, "spe": 47},
        "abilities": ["Sand Stream"],
        "move_tiers": {"Ground": ["Mud Slap", "Earthquake"], "Rock": ["Rock Slide", "Stone Edge"], "Dark": ["Crunch"]},
    },
    "Excadrill": {
        "types": ["Ground", "Steel"],
        "stats": {"hp": 110, "atk": 135, "def": 60, "spa": 50, "spd": 65, "spe": 88},
        "abilities": ["Sand Rush", "Sand Force"],
        "move_tiers": {"Ground": ["Mud Slap", "Dig", "Earthquake"], "Steel": ["Metal Claw", "Iron Head"], "Rock": ["Rock Slide"]},
    },
    "Mamoswine": {
        "types": ["Ice", "Ground"],
        "stats": {"hp": 110, "atk": 130, "def": 80, "spa": 70, "spd": 60, "spe": 80},
        "abilities": ["Thick Fat", "Snow Cloak"],
        "move_tiers": {"Ground": ["Mud Slap", "Earthquake"], "Ice": ["Ice Shard", "Ice Punch"], "Rock": ["Stone Edge"]},
    },
    "Garchomp": {
        "types": ["Dragon", "Ground"],
        "stats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
        "abilities": ["Sand Veil", "Rough Skin"],
        "move_tiers": {"Ground": ["Earthquake"], "Dragon": ["Dragon Claw", "Outrage"], "Rock": ["Stone Edge"], "Fire": ["Fire Blast"]},
    },
    # ══════════ Flying ══════════
    "Pidgey": {
        "types": ["Flying", "Normal"],
        "stats": {"hp": 40, "atk": 45, "def": 40, "spa": 35, "spd": 35, "spe": 56},
        "abilities": ["Adaptability"],
        "move_tiers": {"Normal": ["Quick Attack", "Tackle"], "Flying": ["Gust", "Wing Attack", "Air Slash", "Hurricane", "Brave Bird"], "Dragon": ["Twister"]},
    },
    "Pidgeotto": {
        "types": ["Flying", "Normal"],
        "stats": {"hp": 63, "atk": 60, "def": 55, "spa": 50, "spd": 50, "spe": 71},
        "abilities": ["Adaptability"],
        "move_tiers": {"Normal": ["Quick Attack", "Tackle"], "Flying": ["Gust", "Wing Attack", "Air Slash", "Hurricane", "Brave Bird"], "Dragon": ["Twister"]},
    },
    "Pidgeot": {
        "types": ["Flying", "Normal"],
        "stats": {"hp": 83, "atk": 80, "def": 75, "spa": 70, "spd": 70, "spe": 91},
        "abilities": ["No Guard"],
        "move_tiers": {"Normal": ["Quick Attack", "Tackle"], "Flying": ["Gust", "Wing Attack", "Air Slash", "Hurricane", "Brave Bird"], "Dragon": ["Twister"]},
    },
    # ══════════ Psychic ══════════
    "Alakazam": {
        "types": ["Psychic"],
        "stats": {"hp": 55, "atk": 50, "def": 45, "spa": 135, "spd": 95, "spe": 120},
        "abilities": ["Synchronize", "Magic Guard"],
        "move_tiers": {"Psychic": ["Confusion", "Psyshock", "Psychic"], "Ghost": ["Shadow Ball"], "Grass": ["Energy Ball"], "Fighting": ["Focus Blast"]},
    },
    "Espeon": {
        "types": ["Psychic"],
        "stats": {"hp": 65, "atk": 65, "def": 60, "spa": 130, "spd": 95, "spe": 110},
        "abilities": ["Synchronize", "Magic Bounce"],
        "move_tiers": {"Psychic": ["Confusion", "Psyshock", "Psychic"], "Ghost": ["Shadow Ball"], "Fairy": ["Dazzling Gleam"]},
    },
    "Metagross": {
        "types": ["Steel", "Psychic"],
        "stats": {"hp": 80, "atk": 135, "def": 130, "spa": 95, "spd": 90, "spe": 70},
        "abilities": ["Clear Body"],
        "move_tiers": {"Steel": ["Metal Claw", "Iron Head"], "Psychic": ["Zen Headbutt", "Psychic"], "Ice": ["Ice Punch"], "Ground": ["Earthquake"]},
    },
    # ══════════ Bug ══════════
    "Scizor": {
        "types": ["Bug", "Steel"],
        "stats": {"hp": 70, "atk": 130, "def": 100, "spa": 55, "spd": 80, "spe": 65},
        "abilities": ["Technician", "Swarm"],
        "move_tiers": {"Bug": ["Bug Bite", "X-Scissor"], "Steel": ["Bullet Punch", "Iron Head"], "Fighting": ["Brick Break"]},
    },
    "Heracross": {
        "types": ["Bug", "Fighting"],
        "stats": {"hp": 80, "atk": 125, "def": 75, "spa": 40, "spd": 95, "spe": 85},
        "abilities": ["Swarm", "Guts", "Moxie"],
        "move_tiers": {"Bug": ["Bug Bite", "X-Scissor"], "Fighting": ["Brick Break", "Close Combat"], "Rock": ["Stone Edge"]},
    },
    "Caterpie": {
        "types": ["Bug"],
        "stats": {"hp": 45, "atk": 30, "def": 35, "spa": 20, "spd": 20, "spe": 45},
        "abilities": ["Swarm"],
        "move_tiers": {"Normal": ["Tackle"], "Bug": ["Bug Bite"]},
    },
    "Metapod": {
        "types": ["Bug"],
        "stats": {"hp": 50, "atk": 20, "def": 55, "spa": 25, "spd": 25, "spe": 30},
        "abilities": ["Shed Skin"],
        "move_tiers": {"Normal": ["Tackle"]},
    },
    "Butterfree": {
        "types": ["Bug", "Flying"],
        "stats": {"hp": 60, "atk": 45, "def": 50, "spa": 80, "spd": 80, "spe": 70},
        "abilities": ["Compound Eyes", "Tinted Lens"],
        "move_tiers": {"Flying": ["Gust", "Air Slash"], "Normal": ["Tackle"], "Bug": ["Bug Bite", "Bug Buzz"], "Psychic": ["Confusion", "Psybeam"]},
    },
    "Weedle": {
        "types": ["Bug", "Poison"],
        "stats": {"hp": 40, "atk": 35, "def": 30, "spa": 20, "spd": 20, "spe": 50},
        "abilities": ["Swarm"],
        "move_tiers": {"Poison": ["Poison Sting"]},
    },
    "Kakuna": {
        "types": ["Bug", "Poison"],
        "stats": {"hp": 45, "atk": 25, "def": 50, "spa": 25, "spd": 25, "spe": 35},
        "abilities": ["Shed Skin"],
        "move_tiers": {"Normal": ["Tackle"]},
    },
    "Beedrill": {
        "types": ["Bug", "Poison"],
        "stats": {"hp": 65, "atk": 80, "def": 40, "spa": 45, "spd": 80, "spe": 75},
        "abilities": ["Swarm", "Sniper", "Adaptability"],
        "move_tiers": {"Bug": ["Pin Missile", "X-Scissor", "Bug Buzz"], "Poison": ["Poison Sting", "Poison Jab"], "Dark": ["Brutal Swing"], "Ground": ["Drill Run"]},
    },
    # ══════════ Rock ══════════
    "Tyranitar": {
        "types": ["Rock", "Dark"],
        "stats": {"hp": 100, "atk": 134, "def": 110, "spa": 95, "spd": 100, "spe": 61},
        "abilities": ["Sand Stream"],
        "move_tiers": {"Dark": ["Bite", "Crunch"], "Rock": ["Rock Slide", "Stone Edge"], "Ground": ["Earthquake"], "Fire": ["Fire Blast"]},
    },
    "Aerodactyl": {
        "types": ["Rock", "Flying"],
        "stats": {"hp": 80, "atk": 105, "def": 65, "spa": 60, "spd": 75, "spe": 130},
        "abilities": ["Rock Head", "Pressure"],
        "move_tiers": {"Rock": ["Rock Slide", "Stone Edge"], "Flying": ["Aerial Ace"], "Ground": ["Earthquake"]},
    },
    # ══════════ Ghost ══════════
    "Mismagius": {
        "types": ["Ghost"],
        "stats": {"hp": 60, "atk": 60, "def": 60, "spa": 105, "spd": 105, "spe": 105},
        "abilities": ["Levitate"],
        "move_tiers": {"Ghost": ["Hex", "Shadow Ball"], "Electric": ["Thunderbolt"], "Fairy": ["Dazzling Gleam"]},
    },
    # ══════════ Dragon ══════════
    "Dratini": {
        "types": ["Dragon"],
        "stats": {"hp": 41, "atk": 64, "def": 45, "spa": 50, "spd": 50, "spe": 50},
        "abilities": ["Shed Skin"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Pulse"], "Normal": ["Body Slam"], "Water": ["Aqua Tail"]},
    },
    "Bagon": {
        "types": ["Dragon"],
        "stats": {"hp": 45, "atk": 75, "def": 60, "spa": 40, "spd": 30, "spe": 50},
        "abilities": ["Rock Head"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Claw"], "Normal": ["Tackle", "Body Slam"]},
    },
    "Dragonair": {
        "types": ["Dragon"],
        "stats": {"hp": 61, "atk": 84, "def": 65, "spa": 70, "spd": 70, "spe": 70},
        "abilities": ["Shed Skin"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Pulse", "Outrage"], "Normal": ["Body Slam"], "Fire": ["Flamethrower"]},
    },
    "Shelgon": {
        "types": ["Dragon"],
        "stats": {"hp": 65, "atk": 95, "def": 100, "spa": 60, "spd": 50, "spe": 50},
        "abilities": ["Rock Head"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Claw", "Outrage"], "Normal": ["Body Slam"], "Fire": ["Flamethrower"]},
    },
    "Haxorus": {
        "types": ["Dragon"],
        "stats": {"hp": 76, "atk": 147, "def": 90, "spa": 60, "spd": 70, "spe": 97},
        "abilities": ["Mold Breaker"],
        "move_tiers": {"Dragon": ["Dragon Claw", "Outrage"], "Normal": ["Slash", "Return"], "Ground": ["Earthquake"]},
    },
    "Kingdra": {
        "types": ["Water", "Dragon"],
        "stats": {"hp": 75, "atk": 95, "def": 95, "spa": 95, "spd": 95, "spe": 85},
        "abilities": ["Swift Swim", "Sniper"],
        "move_tiers": {"Dragon": ["Dragon Breath", "Dragon Pulse", "Draco Meteor"], "Water": ["Water Gun", "Surf", "Hydro Pump"], "Ice": ["Ice Beam"]},
    },
    "Dragonite": {
        "types": ["Dragon", "Flying"],
        "stats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80},
        "abilities": ["Inner Focus", "Multiscale"],
        "move_tiers": {"Dragon": ["Dragon Claw", "Outrage"], "Fire": ["Fire Punch", "Flamethrower"], "Normal": ["Extreme Speed"], "Ground": ["Earthquake"]},
    },
    "Salamence": {
        "types": ["Dragon", "Flying"],
        "stats": {"hp": 95, "atk": 135, "def": 80, "spa": 110, "spd": 80, "spe": 100},
        "abilities": ["Intimidate", "Moxie"],
        "move_tiers": {"Dragon": ["Dragon Claw", "Outrage", "Draco Meteor"], "Fire": ["Flamethrower", "Fire Blast"], "Flying": ["Aerial Ace", "Brave Bird"]},
    },
    # ══════════ Dark ══════════
    "Murkrow": {
        "types": ["Dark", "Flying"],
        "stats": {"hp": 60, "atk": 85, "def": 42, "spa": 85, "spd": 42, "spe": 91},
        "abilities": ["Insomnia", "Super Luck"],
        "move_tiers": {"Dark": ["Pursuit", "Dark Pulse"], "Flying": ["Wing Attack", "Brave Bird"]},
    },
    "Sneasel": {
        "types": ["Dark", "Ice"],
        "stats": {"hp": 55, "atk": 95, "def": 55, "spa": 35, "spd": 75, "spe": 115},
        "abilities": ["Inner Focus", "Pressure"],
        "move_tiers": {"Dark": ["Pursuit", "Crunch"], "Ice": ["Ice Shard", "Ice Punch"]},
    },
    "Absol": {
        "types": ["Dark"],
        "stats": {"hp": 65, "atk": 130, "def": 60, "spa": 75, "spd": 60, "spe": 75},
        "abilities": ["Super Luck", "Pressure"],
        "move_tiers": {"Dark": ["Bite", "Crunch", "Dark Pulse"], "Normal": ["Slash", "Return"], "Psychic": ["Zen Headbutt"]},
    },
    "Honchkrow": {
        "types": ["Dark", "Flying"],
        "stats": {"hp": 100, "atk": 125, "def": 52, "spa": 105, "spd": 52, "spe": 71},
        "abilities": ["Insomnia", "Super Luck"],
        "move_tiers": {"Dark": ["Pursuit", "Crunch", "Dark Pulse"], "Flying": ["Wing Attack", "Brave Bird"]},
    },
    "Zoroark": {
        "types": ["Dark"],
        "stats": {"hp": 60, "atk": 105, "def": 60, "spa": 120, "spd": 60, "spe": 105},
        "abilities": ["Illusion"],
        "move_tiers": {"Dark": ["Pursuit", "Dark Pulse"], "Ghost": ["Shadow Ball"], "Fighting": ["Focus Blast"]},
    },
    "Umbreon": {
        "types": ["Dark"],
        "stats": {"hp": 95, "atk": 65, "def": 110, "spa": 60, "spd": 130, "spe": 65},
        "abilities": ["Synchronize", "Inner Focus"],
        "move_tiers": {"Dark": ["Bite", "Dark Pulse"], "Fairy": ["Moonblast"], "Ghost": ["Shadow Ball"]},
    },
    # ══════════ Steel ══════════
    "Aggron": {
        "types": ["Steel", "Rock"],
        "stats": {"hp": 70, "atk": 110, "def": 180, "spa": 60, "spd": 60, "spe": 50},
        "abilities": ["Sturdy", "Rock Head"],
        "move_tiers": {"Steel": ["Metal Claw", "Iron Head", "Iron Tail"], "Rock": ["Rock Slide", "Stone Edge"], "Ground": ["Earthquake"]},
    },
    # ══════════ Fairy ══════════
    "Gardevoir": {
        "types": ["Psychic", "Fairy"],
        "stats": {"hp": 68, "atk": 65, "def": 65, "spa": 125, "spd": 115, "spe": 80},
        "abilities": ["Synchronize", "Trace"],
        "move_tiers": {"Fairy": ["Dazzling Gleam", "Moonblast"], "Psychic": ["Confusion", "Psychic"], "Ghost": ["Shadow Ball"]},
    },
    "Sylveon": {
        "types": ["Fairy"],
        "stats": {"hp": 95, "atk": 65, "def": 65, "spa": 110, "spd": 130, "spe": 60},
        "abilities": ["Cute Charm", "Pixilate"],
        "move_tiers": {"Fairy": ["Fairy Wind", "Dazzling Gleam", "Moonblast"], "Psychic": ["Psyshock"], "Ghost": ["Shadow Ball"]},
    },
    "Togekiss": {
        "types": ["Fairy", "Flying"],
        "stats": {"hp": 85, "atk": 50, "def": 95, "spa": 120, "spd": 115, "spe": 80},
        "abilities": ["Serene Grace", "Hustle"],
        "move_tiers": {"Fairy": ["Fairy Wind", "Dazzling Gleam", "Moonblast"], "Flying": ["Air Slash"], "Fire": ["Flamethrower"]},
    },
    # ══════════ Normal ══════════
    "Snorlax": {
        "types": ["Normal"],
        "stats": {"hp": 160, "atk": 110, "def": 65, "spa": 65, "spd": 110, "spe": 30},
        "abilities": ["Thick Fat", "Immunity"],
        "move_tiers": {"Normal": ["Body Slam", "Return"], "Ground": ["Earthquake"], "Ice": ["Ice Punch"], "Fire": ["Fire Punch"]},
    },
    "Zangoose": {
        "types": ["Normal"],
        "stats": {"hp": 73, "atk": 115, "def": 60, "spa": 60, "spd": 60, "spe": 90},
        "abilities": ["Immunity", "Toxic Boost"],
        "move_tiers": {"Normal": ["Slash", "Facade", "Return"], "Fighting": ["Brick Break", "Close Combat"], "Dark": ["Knock Off"]},
    },
    "Staraptor": {
        "types": ["Normal", "Flying"],
        "stats": {"hp": 85, "atk": 120, "def": 70, "spa": 50, "spd": 60, "spe": 100},
        "abilities": ["Intimidate", "Reckless"],
        "move_tiers": {"Flying": ["Aerial Ace", "Brave Bird"], "Normal": ["Quick Attack", "Return"], "Fighting": ["Close Combat"]},
    },
}

# ─── Evolution Chains ───────────────────────────────────────────────
# Maps species -> its pre-evolution (if any)
EVOLVES_FROM = {
    "Charmeleon": "Charmander",
    "Charizard": "Charmeleon",
    "Arcanine": "Growlithe",
    "Wartortle": "Squirtle",
    "Blastoise": "Wartortle",
    "Raichu": "Pikachu",
    "Sandslash": "Sandshrew",
    "Honchkrow": "Murkrow",
    "Weavile": "Sneasel",
    "Dragonair": "Dratini",
    "Dragonite": "Dragonair",
    "Shelgon": "Bagon",
    "Salamence": "Shelgon",
    "Ivysaur": "Bulbasaur",
    "Venusaur": "Ivysaur",
    "Metapod": "Caterpie",
    "Butterfree": "Metapod",
    "Kakuna": "Weedle",
    "Beedrill": "Kakuna",
    "Pidgeotto": "Pidgey",
    "Pidgeot": "Pidgeotto",
}

# ─── Type Tiers (ordered weakest → strongest) ──────────────────────
# Used by the shop to determine the next Pokemon upgrade for each specialty.
# Each entry must have that type. Non-evolution adds grow the team; evolutions replace.
TYPE_TIERS = {
    "Normal": [
        "Zangoose", "Staraptor", "Snorlax"
    ],
    "Fire": [
        "Charmander", "Growlithe", "Charmeleon", "Flareon",
        "Blaziken", "Charizard", "Magmortar", "Arcanine"
    ],
    "Water": [
        "Squirtle", "Wartortle", "Starmie", "Vaporeon",
        "Blastoise", "Lapras", "Gyarados", "Kingdra",
        "Milotic"
    ],
    "Grass": [
        "Bulbasaur", "Ivysaur", "Roserade", "Venusaur",
        "Sceptile"
    ],
    "Electric": [
        "Pikachu", "Raichu", "Ampharos", "Luxray",
        "Jolteon", "Magnezone", "Electivire"
    ],
    "Ice": [
        "Glaceon", "Mamoswine"
    ],
    "Fighting": [
        "Machamp", "Lucario"
    ],
    "Poison": [
        "Crobat"
    ],
    "Ground": [
        "Sandshrew", "Sandslash", "Excadrill", "Flygon",
        "Hippowdon"
    ],
    "Flying": [
        "Pidgey", "Pidgeotto", "Pidgeot"
    ],
    "Psychic": [
        "Alakazam", "Gardevoir", "Espeon"
    ],
    "Bug": [
        "Caterpie", "Weedle", "Kakuna", "Metapod",
        "Beedrill", "Butterfree", "Heracross", "Scizor"
    ],
    "Rock": [
        "Aerodactyl", "Tyranitar"
    ],
    "Ghost": [
        "Mismagius", "Gengar", "Chandelure"
    ],
    "Dragon": [
        "Bagon", "Dratini", "Dragonair", "Shelgon",
        "Haxorus", "Dragonite", "Garchomp", "Salamence"
    ],
    "Dark": [
        "Murkrow", "Sneasel", "Absol", "Honchkrow",
        "Weavile", "Zoroark", "Umbreon"
    ],
    "Steel": [
        "Aggron", "Metagross"
    ],
    "Fairy": [
        "Sylveon", "Togekiss"
    ],
}


# ─── Default League Configuration ──────────────────────────────────
# Each gym leader/E4 starts small; the player upgrades them via the shop.

DEFAULT_GYM_LEADERS = [
    {
        "name": "Norman",
        "title": "Gym Leader 1",
        "specialty": "Normal",
        "team": [{"species": "Zangoose", "level": 10}],
    },
    {
        "name": "Bugsy",
        "title": "Gym Leader 2",
        "specialty": "Bug",
        "team": [{"species": "Heracross", "level": 13}],
    },
    {
        "name": "Fantina",
        "title": "Gym Leader 3",
        "specialty": "Ghost",
        "team": [{"species": "Mismagius", "level": 16}],
    },
    {
        "name": "Roxanne",
        "title": "Gym Leader 4",
        "specialty": "Rock",
        "team": [{"species": "Aerodactyl", "level": 19}],
    },
    {
        "name": "Janine",
        "title": "Gym Leader 5",
        "specialty": "Poison",
        "team": [{"species": "Bulbasaur", "level": 22}],
    },
    {
        "name": "Candice",
        "title": "Gym Leader 6",
        "specialty": "Ice",
        "team": [{"species": "Sneasel", "level": 25}],
    },
    {
        "name": "Winona",
        "title": "Gym Leader 7",
        "specialty": "Flying",
        "team": [{"species": "Murkrow", "level": 28}],
    },
    {
        "name": "Maylene",
        "title": "Gym Leader 8",
        "specialty": "Fighting",
        "team": [{"species": "Heracross", "level": 30}],
    },
    {
        "name": "Terra",
        "title": "Gym Leader 9",
        "specialty": "Ground",
        "team": [{"species": "Sandshrew", "level": 32}],
    },
    {
        "name": "Sabrina",
        "title": "Gym Leader 10",
        "specialty": "Psychic",
        "team": [{"species": "Alakazam", "level": 34}],
    },
    {
        "name": "Raven",
        "title": "Gym Leader 11",
        "specialty": "Dark",
        "team": [{"species": "Murkrow", "level": 36}],
    },
    {
        "name": "Jasmine",
        "title": "Gym Leader 12",
        "specialty": "Steel",
        "team": [{"species": "Scizor", "level": 38}],
    },
    {
        "name": "Valerie",
        "title": "Gym Leader 13",
        "specialty": "Fairy",
        "team": [{"species": "Gardevoir", "level": 40}],
    },
    {
        "name": "Drake",
        "title": "Gym Leader 14",
        "specialty": "Dragon",
        "team": [{"species": "Bagon", "level": 42}],
    },
]

DEFAULT_ELITE_FOUR = [
    {
        "name": "Flint",
        "title": "Elite Four 1",
        "specialty": "Fire",
        "team": [
            {"species": "Charmander", "level": 45},
            {"species": "Growlithe", "level": 47},
        ],
    },
    {
        "name": "Marina",
        "title": "Elite Four 2",
        "specialty": "Water",
        "team": [
            {"species": "Squirtle", "level": 48},
            {"species": "Starmie", "level": 50},
        ],
    },
    {
        "name": "Gardenia",
        "title": "Elite Four 3",
        "specialty": "Grass",
        "team": [
            {"species": "Bulbasaur", "level": 51},
            {"species": "Roserade", "level": 53},
        ],
    },
    {
        "name": "Surge",
        "title": "Elite Four 4",
        "specialty": "Electric",
        "team": [
            {"species": "Pikachu", "level": 54},
            {"species": "Ampharos", "level": 56},
        ],
    },
]

# ─── Challenger Name Parts ──────────────────────────────────────────
CHALLENGER_FIRST_NAMES = [
    "Ace", "Bug Catcher", "Lass", "Youngster", "Hiker", "Beauty",
    "Sailor", "Fisherman", "Psychic", "Ranger", "Swimmer", "Camper",
    "Picnicker", "Cool Trainer", "Veteran", "Black Belt",
]

CHALLENGER_LAST_NAMES = [
    "Joey", "Misty", "Brock", "Gary", "Dawn", "May", "Ash", "Red",
    "Blue", "Ethan", "Silver", "Lyra", "Nate", "Rosa", "Hilda",
    "Hilbert", "Calem", "Serena", "Elio", "Selene", "Victor", "Gloria",
]

# Pokemon pools by rough difficulty tier (for challenger generation)
CHALLENGER_POKEMON_TIERS = {
    "weak": [
        "Charmander", "Squirtle", "Bulbasaur", "Pikachu", "Zangoose",
    ],
    "medium": [
        "Arcanine", "Vaporeon", "Jolteon", "Sceptile", "Roserade",
        "Crobat", "Staraptor", "Heracross", "Machamp", "Absol",
        "Luxray", "Mismagius", "Glaceon", "Espeon", "Aerodactyl",
    ],
    "strong": [
        "Gyarados", "Gengar", "Alakazam", "Garchomp", "Dragonite",
        "Salamence", "Tyranitar", "Metagross", "Scizor", "Blaziken",
        "Togekiss", "Lucario", "Chandelure", "Gardevoir", "Weavile",
        "Lapras", "Snorlax", "Sylveon", "Aggron", "Flygon", "Umbreon",
    ],
}
