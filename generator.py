"""
Pokemon League Champion - Challenger Generator
Procedurally generates challengers with scaling difficulty.
Tiers are auto-built from base stat totals — never needs manual updates.
"""
import random
import math
from data import (
    POKEMON_DB, MOVES_DB,
    CHALLENGER_FIRST_NAMES, CHALLENGER_LAST_NAMES,
)


# ─── Auto-build Pokemon tiers from Base Stat Totals ────────────────

def _build_challenger_tiers():
    """Sort all POKEMON_DB species into 5 tiers by base stat total."""
    species_bst = []
    for name, data in POKEMON_DB.items():
        stats = data.get("stats", {})
        bst = sum(stats.values())
        species_bst.append((name, bst))
    species_bst.sort(key=lambda x: x[1])

    n = len(species_bst)
    # Tier boundaries (percentiles): weak / below_avg / average / strong / elite
    cuts = [
        int(n * 0.20),  # bottom 20 %
        int(n * 0.40),  # 20-40 %
        int(n * 0.65),  # 40-65 %
        int(n * 0.85),  # 65-85 %
    ]
    tiers = {
        "weak":      [s for s, _ in species_bst[:cuts[0]]],
        "below_avg": [s for s, _ in species_bst[cuts[0]:cuts[1]]],
        "average":   [s for s, _ in species_bst[cuts[1]:cuts[2]]],
        "strong":    [s for s, _ in species_bst[cuts[2]:cuts[3]]],
        "elite":     [s for s, _ in species_bst[cuts[3]:]],
    }
    # Make sure every tier has at least 1 entry (fallback to full list)
    for k in tiers:
        if not tiers[k]:
            tiers[k] = [s for s, _ in species_bst]
    return tiers


CHALLENGER_TIERS = _build_challenger_tiers()


# ─── Tier pool selection ────────────────────────────────────────────

def _get_pool(challenger_number):
    """Return a weighted pool of species appropriate for this stage."""
    t = CHALLENGER_TIERS
    if challenger_number < 3:
        return t["weak"]
    elif challenger_number < 6:
        return t["weak"] + t["below_avg"]
    elif challenger_number < 10:
        return t["below_avg"] + t["average"]
    elif challenger_number < 15:
        return t["average"] + t["strong"]
    elif challenger_number < 22:
        return t["strong"] + t["elite"]
    else:
        return t["strong"] + t["elite"] * 2  # bias towards elite late game


# ─── Team size ──────────────────────────────────────────────────────

def _team_size(challenger_number):
    """Determine team size with slight randomness."""
    if challenger_number < 2:
        return 1
    elif challenger_number < 5:
        return random.choice([1, 2, 2])
    elif challenger_number < 9:
        return random.choice([2, 2, 3, 3])
    elif challenger_number < 14:
        return random.choice([3, 3, 3, 4])
    elif challenger_number < 20:
        return random.choice([3, 4, 4, 5])
    else:
        return random.choice([4, 4, 5, 5, 6])


# ─── Level calculation ──────────────────────────────────────────────

def _challenger_level(challenger_number):
    """
    Compute a level with weighted randomness.
    Trend upward over time but with variance so challengers aren't
    strictly harder each time.
    """
    # Base curve: starts at ~1, approaches 60-65 slowly
    base = 1 + challenger_number * 1.6
    base = min(base, 62)

    # Variance grows with progression (±20 % of base, at least ±1)
    variance = max(1, int(base * 0.22))
    level = base + random.randint(-variance, variance)

    # Soft floor / ceiling
    level = max(1, min(65, int(level)))
    return level


# ─── Move selection proportional to level ───────────────────────────

def _pick_moves(species, level):
    """
    Pick moves using the move_tiers system.
    Higher level → unlocks deeper tiers & more move slots.
    """
    pdata = POKEMON_DB[species]
    move_tiers = pdata.get("move_tiers", {})

    # How deep into each type's tier list we can go (0.0 – 1.0)
    tier_progress = min(1.0, level / 55.0)

    available = []
    for mtype, tier_list in move_tiers.items():
        # Number of moves unlocked from this type's tier
        unlocked = max(1, int(math.ceil(len(tier_list) * tier_progress)))
        # Pick the highest unlocked move (strongest available)
        best = tier_list[unlocked - 1]
        available.append(best)

    if not available:
        available = ["Tackle"]

    # Number of move slots scales with level
    if level < 8:
        slots = 1
    elif level < 18:
        slots = 2
    elif level < 32:
        slots = min(3, len(available))
    else:
        slots = min(4, len(available))

    # Use the best moves, but shuffle slightly for variety
    random.shuffle(available)
    return available[:slots]


# ─── Title variety ──────────────────────────────────────────────────

def _challenger_title(challenger_number):
    """Give tougher challengers fancier titles."""
    if challenger_number < 5:
        return random.choice(["Challenger", "Trainer", "Rookie"])
    elif challenger_number < 12:
        return random.choice(["Challenger", "Trainer", "Rival"])
    elif challenger_number < 20:
        return random.choice(["Ace Trainer", "Veteran", "Expert"])
    else:
        return random.choice(["Ace Trainer", "Veteran", "Elite Trainer",
                              "Pokemon Master"])


# ─── Main entry point ──────────────────────────────────────────────

def generate_challenger(challenger_number):
    """
    Generate a procedurally created challenger.
    Difficulty scales with challenger_number (how many beaten so far).
    """
    name = (f"{random.choice(CHALLENGER_FIRST_NAMES)} "
            f"{random.choice(CHALLENGER_LAST_NAMES)}")
    title = _challenger_title(challenger_number)

    pool = _get_pool(challenger_number)
    size = _team_size(challenger_number)

    team_data = []
    chosen = random.sample(pool, min(size, len(pool)))

    for species in chosen:
        level = _challenger_level(challenger_number)
        moves = _pick_moves(species, level)
        team_data.append({
            "species": species,
            "level": level,
            "moves": moves,
        })

    return {
        "name": name,
        "title": title,
        "team": team_data,
    }
