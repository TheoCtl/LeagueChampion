"""
Pokemon League Champion - Challenger Generator
Procedurally generates challengers with scaling difficulty.
"""
import random
from data import (
    POKEMON_DB, MOVES_DB,
    CHALLENGER_FIRST_NAMES, CHALLENGER_LAST_NAMES,
    CHALLENGER_POKEMON_TIERS,
)


def generate_challenger(challenger_number):
    """
    Generate a procedurally created challenger.
    Difficulty scales with challenger_number (how many you've beaten so far).
    """
    name = f"{random.choice(CHALLENGER_FIRST_NAMES)} {random.choice(CHALLENGER_LAST_NAMES)}"

    # Scale difficulty
    # Early challengers: 1 weak pokemon, low level
    # Later challengers: more pokemon, stronger species, higher levels
    base_level = min(8 + challenger_number * 2, 55)
    level_variance = max(1, challenger_number // 2)

    # Determine team size (1-4 based on challenger number)
    if challenger_number < 3:
        team_size = 1
    elif challenger_number < 6:
        team_size = 2
    elif challenger_number < 10:
        team_size = 3
    elif challenger_number < 15:
        team_size = random.randint(3, 4)
    else:
        team_size = random.randint(4, 6)

    # Determine which tier(s) to pull from
    if challenger_number < 4:
        pool = CHALLENGER_POKEMON_TIERS["weak"]
    elif challenger_number < 8:
        pool = CHALLENGER_POKEMON_TIERS["weak"] + CHALLENGER_POKEMON_TIERS["medium"]
    elif challenger_number < 12:
        pool = CHALLENGER_POKEMON_TIERS["medium"]
    else:
        pool = CHALLENGER_POKEMON_TIERS["medium"] + CHALLENGER_POKEMON_TIERS["strong"]

    # Build team
    team_data = []
    chosen_species = random.sample(pool, min(team_size, len(pool)))

    for species in chosen_species:
        level = base_level + random.randint(-level_variance, level_variance)
        level = max(5, level)
        poke_data = POKEMON_DB[species]
        # Derive available moves from move_tiers (flatten all tiers)
        available_moves = []
        for tier_list in poke_data.get("move_tiers", {}).values():
            available_moves.extend(tier_list)
        available_moves = list(dict.fromkeys(available_moves))  # dedupe, keep order
        if not available_moves:
            available_moves = ["Tackle"]

        # Number of moves scales with level
        if level < 15:
            num_moves = 2
        elif level < 30:
            num_moves = min(3, len(available_moves))
        else:
            num_moves = min(4, len(available_moves))

        moves = available_moves[:num_moves]

        team_data.append({
            "species": species,
            "level": level,
            "moves": moves,
        })

    return {
        "name": name,
        "title": "Challenger",
        "team": team_data,
    }
