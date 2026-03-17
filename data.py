"""
Pokemon League Champion - Game Data
All Pokemon stats, moves, type charts, and starter configurations.
"""

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
# Each move: {name, type, category (physical/special), power, accuracy, pp}

MOVES_DB = {
    # Normal
    "Tackle": {"type": "Normal", "category": "physical", "power": 40, "accuracy": 100},
    "Quick Attack": {"type": "Normal", "category": "physical", "power": 40, "accuracy": 100},
    "Body Slam": {"type": "Normal", "category": "physical", "power": 85, "accuracy": 100},
    "Hyper Beam": {"type": "Normal", "category": "special", "power": 150, "accuracy": 90},
    "Slash": {"type": "Normal", "category": "physical", "power": 70, "accuracy": 100},
    # Fire
    "Ember": {"type": "Fire", "category": "special", "power": 40, "accuracy": 100},
    "Flamethrower": {"type": "Fire", "category": "special", "power": 90, "accuracy": 100},
    "Fire Blast": {"type": "Fire", "category": "special", "power": 110, "accuracy": 85},
    "Fire Punch": {"type": "Fire", "category": "physical", "power": 75, "accuracy": 100},
    "Blaze Kick": {"type": "Fire", "category": "physical", "power": 85, "accuracy": 90},
    # Water
    "Water Gun": {"type": "Water", "category": "special", "power": 40, "accuracy": 100},
    "Surf": {"type": "Water", "category": "special", "power": 90, "accuracy": 100},
    "Hydro Pump": {"type": "Water", "category": "special", "power": 110, "accuracy": 80},
    "Aqua Tail": {"type": "Water", "category": "physical", "power": 90, "accuracy": 90},
    "Waterfall": {"type": "Water", "category": "physical", "power": 80, "accuracy": 100},
    # Grass
    "Vine Whip": {"type": "Grass", "category": "physical", "power": 45, "accuracy": 100},
    "Razor Leaf": {"type": "Grass", "category": "physical", "power": 55, "accuracy": 95},
    "Solar Beam": {"type": "Grass", "category": "special", "power": 120, "accuracy": 100},
    "Energy Ball": {"type": "Grass", "category": "special", "power": 90, "accuracy": 100},
    "Leaf Blade": {"type": "Grass", "category": "physical", "power": 90, "accuracy": 100},
    # Electric
    "Thunder Shock": {"type": "Electric", "category": "special", "power": 40, "accuracy": 100},
    "Thunderbolt": {"type": "Electric", "category": "special", "power": 90, "accuracy": 100},
    "Thunder": {"type": "Electric", "category": "special", "power": 110, "accuracy": 70},
    "Spark": {"type": "Electric", "category": "physical", "power": 65, "accuracy": 100},
    "Wild Charge": {"type": "Electric", "category": "physical", "power": 90, "accuracy": 100},
    # Ice
    "Ice Shard": {"type": "Ice", "category": "physical", "power": 40, "accuracy": 100},
    "Ice Beam": {"type": "Ice", "category": "special", "power": 90, "accuracy": 100},
    "Blizzard": {"type": "Ice", "category": "special", "power": 110, "accuracy": 70},
    "Ice Punch": {"type": "Ice", "category": "physical", "power": 75, "accuracy": 100},
    # Fighting
    "Karate Chop": {"type": "Fighting", "category": "physical", "power": 50, "accuracy": 100},
    "Close Combat": {"type": "Fighting", "category": "physical", "power": 120, "accuracy": 100},
    "Aura Sphere": {"type": "Fighting", "category": "special", "power": 80, "accuracy": 100},
    "Brick Break": {"type": "Fighting", "category": "physical", "power": 75, "accuracy": 100},
    # Poison
    "Poison Sting": {"type": "Poison", "category": "physical", "power": 15, "accuracy": 100},
    "Sludge Bomb": {"type": "Poison", "category": "special", "power": 90, "accuracy": 100},
    "Cross Poison": {"type": "Poison", "category": "physical", "power": 70, "accuracy": 100},
    # Ground
    "Mud Slap": {"type": "Ground", "category": "special", "power": 20, "accuracy": 100},
    "Earthquake": {"type": "Ground", "category": "physical", "power": 100, "accuracy": 100},
    "Dig": {"type": "Ground", "category": "physical", "power": 80, "accuracy": 100},
    "Earth Power": {"type": "Ground", "category": "special", "power": 90, "accuracy": 100},
    # Flying
    "Gust": {"type": "Flying", "category": "special", "power": 40, "accuracy": 100},
    "Air Slash": {"type": "Flying", "category": "special", "power": 75, "accuracy": 95},
    "Brave Bird": {"type": "Flying", "category": "physical", "power": 120, "accuracy": 100},
    "Aerial Ace": {"type": "Flying", "category": "physical", "power": 60, "accuracy": 100},
    # Psychic
    "Confusion": {"type": "Psychic", "category": "special", "power": 50, "accuracy": 100},
    "Psychic": {"type": "Psychic", "category": "special", "power": 90, "accuracy": 100},
    "Psyshock": {"type": "Psychic", "category": "special", "power": 80, "accuracy": 100},
    "Zen Headbutt": {"type": "Psychic", "category": "physical", "power": 80, "accuracy": 90},
    # Bug
    "Bug Bite": {"type": "Bug", "category": "physical", "power": 60, "accuracy": 100},
    "X-Scissor": {"type": "Bug", "category": "physical", "power": 80, "accuracy": 100},
    "Signal Beam": {"type": "Bug", "category": "special", "power": 75, "accuracy": 100},
    # Rock
    "Rock Throw": {"type": "Rock", "category": "physical", "power": 50, "accuracy": 90},
    "Rock Slide": {"type": "Rock", "category": "physical", "power": 75, "accuracy": 90},
    "Stone Edge": {"type": "Rock", "category": "physical", "power": 100, "accuracy": 80},
    # Ghost
    "Shadow Ball": {"type": "Ghost", "category": "special", "power": 80, "accuracy": 100},
    "Shadow Claw": {"type": "Ghost", "category": "physical", "power": 70, "accuracy": 100},
    "Hex": {"type": "Ghost", "category": "special", "power": 65, "accuracy": 100},
    # Dragon
    "Dragon Claw": {"type": "Dragon", "category": "physical", "power": 80, "accuracy": 100},
    "Dragon Pulse": {"type": "Dragon", "category": "special", "power": 85, "accuracy": 100},
    "Outrage": {"type": "Dragon", "category": "physical", "power": 120, "accuracy": 100},
    "Draco Meteor": {"type": "Dragon", "category": "special", "power": 130, "accuracy": 90},
    # Dark
    "Bite": {"type": "Dark", "category": "physical", "power": 60, "accuracy": 100},
    "Crunch": {"type": "Dark", "category": "physical", "power": 80, "accuracy": 100},
    "Dark Pulse": {"type": "Dark", "category": "special", "power": 80, "accuracy": 100},
    # Steel
    "Iron Tail": {"type": "Steel", "category": "physical", "power": 100, "accuracy": 75},
    "Flash Cannon": {"type": "Steel", "category": "special", "power": 80, "accuracy": 100},
    "Metal Claw": {"type": "Steel", "category": "physical", "power": 50, "accuracy": 95},
    # Fairy
    "Fairy Wind": {"type": "Fairy", "category": "special", "power": 40, "accuracy": 100},
    "Moonblast": {"type": "Fairy", "category": "special", "power": 95, "accuracy": 100},
    "Dazzling Gleam": {"type": "Fairy", "category": "special", "power": 80, "accuracy": 100},
    "Play Rough": {"type": "Fairy", "category": "physical", "power": 90, "accuracy": 90},
}


# ─── Pokemon Data ───────────────────────────────────────────────────
# base_hp, base_atk, base_def, base_spa, base_spd, base_spe
# learnable_moves: moves available to learn (first 2 are default at low level)

POKEMON_DB = {
    # ── Fire ──
    "Charmander": {
        "types": ["Fire"],
        "stats": {"hp": 39, "atk": 52, "def": 43, "spa": 60, "spd": 50, "spe": 65},
        "learnable_moves": ["Ember", "Slash", "Flamethrower", "Fire Blast"],
    },
    "Arcanine": {
        "types": ["Fire"],
        "stats": {"hp": 90, "atk": 110, "def": 80, "spa": 100, "spd": 80, "spe": 95},
        "learnable_moves": ["Fire Punch", "Flamethrower", "Fire Blast", "Body Slam"],
    },
    "Blaziken": {
        "types": ["Fire", "Fighting"],
        "stats": {"hp": 80, "atk": 120, "def": 70, "spa": 110, "spd": 70, "spe": 80},
        "learnable_moves": ["Blaze Kick", "Flamethrower", "Close Combat", "Brave Bird"],
    },
    # ── Water ──
    "Squirtle": {
        "types": ["Water"],
        "stats": {"hp": 44, "atk": 48, "def": 65, "spa": 50, "spd": 64, "spe": 43},
        "learnable_moves": ["Water Gun", "Tackle", "Surf", "Hydro Pump"],
    },
    "Gyarados": {
        "types": ["Water", "Flying"],
        "stats": {"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81},
        "learnable_moves": ["Waterfall", "Aqua Tail", "Crunch", "Ice Beam"],
    },
    "Vaporeon": {
        "types": ["Water"],
        "stats": {"hp": 130, "atk": 65, "def": 60, "spa": 110, "spd": 95, "spe": 65},
        "learnable_moves": ["Water Gun", "Surf", "Ice Beam", "Hydro Pump"],
    },
    # ── Grass ──
    "Bulbasaur": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        "learnable_moves": ["Vine Whip", "Tackle", "Razor Leaf", "Solar Beam"],
    },
    "Roserade": {
        "types": ["Grass", "Poison"],
        "stats": {"hp": 60, "atk": 70, "def": 65, "spa": 125, "spd": 105, "spe": 90},
        "learnable_moves": ["Energy Ball", "Sludge Bomb", "Dazzling Gleam", "Shadow Ball"],
    },
    "Sceptile": {
        "types": ["Grass"],
        "stats": {"hp": 70, "atk": 85, "def": 65, "spa": 105, "spd": 85, "spe": 120},
        "learnable_moves": ["Leaf Blade", "Energy Ball", "Dragon Claw", "Quick Attack"],
    },
    # ── Electric ──
    "Pikachu": {
        "types": ["Electric"],
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "learnable_moves": ["Thunder Shock", "Quick Attack", "Thunderbolt", "Spark"],
    },
    "Jolteon": {
        "types": ["Electric"],
        "stats": {"hp": 65, "atk": 65, "def": 60, "spa": 110, "spd": 95, "spe": 130},
        "learnable_moves": ["Thunder Shock", "Thunderbolt", "Thunder", "Shadow Ball"],
    },
    "Luxray": {
        "types": ["Electric"],
        "stats": {"hp": 80, "atk": 120, "def": 79, "spa": 95, "spd": 79, "spe": 70},
        "learnable_moves": ["Spark", "Wild Charge", "Crunch", "Ice Punch"],
    },
    # ── Ice ──
    "Lapras": {
        "types": ["Water", "Ice"],
        "stats": {"hp": 130, "atk": 85, "def": 80, "spa": 85, "spd": 95, "spe": 60},
        "learnable_moves": ["Ice Beam", "Surf", "Hydro Pump", "Body Slam"],
    },
    "Glaceon": {
        "types": ["Ice"],
        "stats": {"hp": 65, "atk": 60, "def": 110, "spa": 130, "spd": 95, "spe": 65},
        "learnable_moves": ["Ice Shard", "Ice Beam", "Blizzard", "Shadow Ball"],
    },
    "Weavile": {
        "types": ["Dark", "Ice"],
        "stats": {"hp": 70, "atk": 120, "def": 65, "spa": 45, "spd": 85, "spe": 125},
        "learnable_moves": ["Ice Shard", "Ice Punch", "Crunch", "X-Scissor"],
    },
    # ── Fighting ──
    "Machamp": {
        "types": ["Fighting"],
        "stats": {"hp": 90, "atk": 130, "def": 80, "spa": 65, "spd": 85, "spe": 55},
        "learnable_moves": ["Karate Chop", "Close Combat", "Rock Slide", "Brick Break"],
    },
    "Lucario": {
        "types": ["Fighting", "Steel"],
        "stats": {"hp": 70, "atk": 110, "def": 70, "spa": 115, "spd": 70, "spe": 90},
        "learnable_moves": ["Aura Sphere", "Close Combat", "Flash Cannon", "Dark Pulse"],
    },
    # ── Poison ──
    "Gengar": {
        "types": ["Ghost", "Poison"],
        "stats": {"hp": 60, "atk": 65, "def": 60, "spa": 130, "spd": 75, "spe": 110},
        "learnable_moves": ["Shadow Ball", "Sludge Bomb", "Dark Pulse", "Thunderbolt"],
    },
    "Crobat": {
        "types": ["Poison", "Flying"],
        "stats": {"hp": 85, "atk": 90, "def": 80, "spa": 70, "spd": 80, "spe": 130},
        "learnable_moves": ["Cross Poison", "Air Slash", "Bite", "X-Scissor"],
    },
    # ── Ground ──
    "Garchomp": {
        "types": ["Dragon", "Ground"],
        "stats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
        "learnable_moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Crunch"],
    },
    "Flygon": {
        "types": ["Ground", "Dragon"],
        "stats": {"hp": 80, "atk": 100, "def": 80, "spa": 80, "spd": 80, "spe": 100},
        "learnable_moves": ["Earthquake", "Dragon Claw", "Rock Slide", "Earth Power"],
    },
    # ── Flying ──
    "Staraptor": {
        "types": ["Normal", "Flying"],
        "stats": {"hp": 85, "atk": 120, "def": 70, "spa": 50, "spd": 60, "spe": 100},
        "learnable_moves": ["Brave Bird", "Aerial Ace", "Close Combat", "Quick Attack"],
    },
    "Togekiss": {
        "types": ["Fairy", "Flying"],
        "stats": {"hp": 85, "atk": 50, "def": 95, "spa": 120, "spd": 115, "spe": 80},
        "learnable_moves": ["Air Slash", "Dazzling Gleam", "Aura Sphere", "Flamethrower"],
    },
    # ── Psychic ──
    "Alakazam": {
        "types": ["Psychic"],
        "stats": {"hp": 55, "atk": 50, "def": 45, "spa": 135, "spd": 95, "spe": 120},
        "learnable_moves": ["Psychic", "Shadow Ball", "Energy Ball", "Dazzling Gleam"],
    },
    "Espeon": {
        "types": ["Psychic"],
        "stats": {"hp": 65, "atk": 65, "def": 60, "spa": 130, "spd": 95, "spe": 110},
        "learnable_moves": ["Psychic", "Psyshock", "Shadow Ball", "Dazzling Gleam"],
    },
    "Metagross": {
        "types": ["Steel", "Psychic"],
        "stats": {"hp": 80, "atk": 135, "def": 130, "spa": 95, "spd": 90, "spe": 70},
        "learnable_moves": ["Zen Headbutt", "Metal Claw", "Earthquake", "Ice Punch"],
    },
    # ── Bug ──
    "Scizor": {
        "types": ["Bug", "Steel"],
        "stats": {"hp": 70, "atk": 130, "def": 100, "spa": 55, "spd": 80, "spe": 65},
        "learnable_moves": ["X-Scissor", "Bug Bite", "Metal Claw", "Brick Break"],
    },
    "Heracross": {
        "types": ["Bug", "Fighting"],
        "stats": {"hp": 80, "atk": 125, "def": 75, "spa": 40, "spd": 95, "spe": 85},
        "learnable_moves": ["X-Scissor", "Close Combat", "Stone Edge", "Aerial Ace"],
    },
    # ── Rock ──
    "Tyranitar": {
        "types": ["Rock", "Dark"],
        "stats": {"hp": 100, "atk": 134, "def": 110, "spa": 95, "spd": 100, "spe": 61},
        "learnable_moves": ["Stone Edge", "Crunch", "Earthquake", "Fire Blast"],
    },
    "Aerodactyl": {
        "types": ["Rock", "Flying"],
        "stats": {"hp": 80, "atk": 105, "def": 65, "spa": 60, "spd": 75, "spe": 130},
        "learnable_moves": ["Rock Slide", "Aerial Ace", "Crunch", "Earthquake"],
    },
    # ── Ghost ──
    "Chandelure": {
        "types": ["Ghost", "Fire"],
        "stats": {"hp": 60, "atk": 55, "def": 90, "spa": 145, "spd": 90, "spe": 80},
        "learnable_moves": ["Shadow Ball", "Flamethrower", "Energy Ball", "Dark Pulse"],
    },
    "Mismagius": {
        "types": ["Ghost"],
        "stats": {"hp": 60, "atk": 60, "def": 60, "spa": 105, "spd": 105, "spe": 105},
        "learnable_moves": ["Shadow Ball", "Hex", "Thunderbolt", "Dazzling Gleam"],
    },
    # ── Dragon ──
    "Dragonite": {
        "types": ["Dragon", "Flying"],
        "stats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80},
        "learnable_moves": ["Dragon Claw", "Outrage", "Flamethrower", "Ice Beam"],
    },
    "Salamence": {
        "types": ["Dragon", "Flying"],
        "stats": {"hp": 95, "atk": 135, "def": 80, "spa": 110, "spd": 80, "spe": 100},
        "learnable_moves": ["Dragon Claw", "Flamethrower", "Hydro Pump", "Draco Meteor"],
    },
    # ── Dark ──
    "Umbreon": {
        "types": ["Dark"],
        "stats": {"hp": 95, "atk": 65, "def": 110, "spa": 60, "spd": 130, "spe": 65},
        "learnable_moves": ["Dark Pulse", "Moonblast", "Shadow Ball", "Body Slam"],
    },
    "Absol": {
        "types": ["Dark"],
        "stats": {"hp": 65, "atk": 130, "def": 60, "spa": 75, "spd": 60, "spe": 75},
        "learnable_moves": ["Crunch", "Dark Pulse", "Slash", "Ice Beam"],
    },
    # ── Steel ──
    "Aggron": {
        "types": ["Steel", "Rock"],
        "stats": {"hp": 70, "atk": 110, "def": 180, "spa": 60, "spd": 60, "spe": 50},
        "learnable_moves": ["Iron Tail", "Stone Edge", "Earthquake", "Ice Punch"],
    },
    # ── Fairy ──
    "Gardevoir": {
        "types": ["Psychic", "Fairy"],
        "stats": {"hp": 68, "atk": 65, "def": 65, "spa": 125, "spd": 115, "spe": 80},
        "learnable_moves": ["Moonblast", "Psychic", "Shadow Ball", "Thunderbolt"],
    },
    "Sylveon": {
        "types": ["Fairy"],
        "stats": {"hp": 95, "atk": 65, "def": 65, "spa": 110, "spd": 130, "spe": 60},
        "learnable_moves": ["Moonblast", "Dazzling Gleam", "Shadow Ball", "Psyshock"],
    },
    # ── Normal ──
    "Snorlax": {
        "types": ["Normal"],
        "stats": {"hp": 160, "atk": 110, "def": 65, "spa": 65, "spd": 110, "spe": 30},
        "learnable_moves": ["Body Slam", "Earthquake", "Ice Punch", "Fire Punch"],
    },
    "Zangoose": {
        "types": ["Normal"],
        "stats": {"hp": 73, "atk": 115, "def": 60, "spa": 60, "spd": 60, "spe": 90},
        "learnable_moves": ["Slash", "Close Combat", "X-Scissor", "Quick Attack"],
    },
}


# ─── Default League Configuration ──────────────────────────────────
# 4 Gym Leaders, 2 Elite Four, Champion (player picks their team)

DEFAULT_GYM_LEADERS = [
    {
        "name": "Flint",
        "title": "Gym Leader 1",
        "specialty": "Fire",
        "team": [
            {"species": "Charmander", "level": 12, "moves": ["Ember", "Slash"]},
        ],
    },
    {
        "name": "Marina",
        "title": "Gym Leader 2",
        "specialty": "Water",
        "team": [
            {"species": "Squirtle", "level": 16, "moves": ["Water Gun", "Tackle"]},
            {"species": "Vaporeon", "level": 18, "moves": ["Water Gun", "Surf"]},
        ],
    },
    {
        "name": "Surge",
        "title": "Gym Leader 3",
        "specialty": "Electric",
        "team": [
            {"species": "Pikachu", "level": 22, "moves": ["Thunder Shock", "Quick Attack"]},
            {"species": "Luxray", "level": 24, "moves": ["Spark", "Crunch"]},
        ],
    },
    {
        "name": "Terra",
        "title": "Gym Leader 4",
        "specialty": "Ground",
        "team": [
            {"species": "Flygon", "level": 28, "moves": ["Earthquake", "Dragon Claw"]},
            {"species": "Garchomp", "level": 30, "moves": ["Earthquake", "Dragon Claw"]},
        ],
    },
]

DEFAULT_ELITE_FOUR = [
    {
        "name": "Raven",
        "title": "Elite Four 1",
        "specialty": "Dark",
        "team": [
            {"species": "Umbreon", "level": 38, "moves": ["Dark Pulse", "Shadow Ball"]},
            {"species": "Weavile", "level": 40, "moves": ["Ice Punch", "Crunch"]},
            {"species": "Absol", "level": 42, "moves": ["Crunch", "Slash"]},
        ],
    },
    {
        "name": "Drake",
        "title": "Elite Four 2",
        "specialty": "Dragon",
        "team": [
            {"species": "Flygon", "level": 44, "moves": ["Earthquake", "Dragon Claw"]},
            {"species": "Salamence", "level": 46, "moves": ["Dragon Claw", "Flamethrower"]},
            {"species": "Dragonite", "level": 48, "moves": ["Dragon Claw", "Ice Beam"]},
        ],
    },
]

# Champion starter options (player picks one set at game start)
CHAMPION_STARTER_OPTIONS = [
    {
        "label": "Balanced",
        "team": [
            {"species": "Arcanine", "level": 50, "moves": ["Flamethrower", "Fire Blast"]},
            {"species": "Gyarados", "level": 50, "moves": ["Waterfall", "Ice Beam"]},
            {"species": "Garchomp", "level": 52, "moves": ["Earthquake", "Dragon Claw", "Stone Edge"]},
        ],
    },
    {
        "label": "Offensive",
        "team": [
            {"species": "Gengar", "level": 50, "moves": ["Shadow Ball", "Sludge Bomb", "Thunderbolt"]},
            {"species": "Alakazam", "level": 50, "moves": ["Psychic", "Shadow Ball", "Energy Ball"]},
            {"species": "Blaziken", "level": 52, "moves": ["Blaze Kick", "Close Combat", "Brave Bird"]},
        ],
    },
    {
        "label": "Defensive",
        "team": [
            {"species": "Snorlax", "level": 50, "moves": ["Body Slam", "Earthquake", "Ice Punch"]},
            {"species": "Metagross", "level": 50, "moves": ["Zen Headbutt", "Metal Claw", "Earthquake"]},
            {"species": "Togekiss", "level": 52, "moves": ["Air Slash", "Dazzling Gleam", "Aura Sphere"]},
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
