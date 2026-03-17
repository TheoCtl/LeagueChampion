"""
Pokemon League Champion - Battle Logic (pure, no UI)
Provides damage calculation, AI, and move execution returning data only.
"""
import random
from data import MOVES_DB, get_type_multiplier


def calc_damage(attacker, defender, move_data):
    """Calculate damage. Returns (damage, type_multiplier)."""
    level = attacker.level
    power = move_data["power"]

    if move_data["category"] == "physical":
        atk_stat = attacker.atk
        def_stat = defender.defense
    else:
        atk_stat = attacker.spa
        def_stat = defender.spd

    base = ((2 * level / 5 + 2) * power * atk_stat / def_stat) / 50 + 2
    type_mult = get_type_multiplier(move_data["type"], defender.types)
    stab = 1.5 if move_data["type"] in attacker.types else 1.0
    rand_factor = random.randint(85, 100) / 100.0
    damage = int(base * type_mult * stab * rand_factor)
    return max(1, damage), type_mult


def ai_choose_move(pokemon, opponent):
    """AI: pick the move that would deal the most expected damage."""
    best_move = None
    best_score = -1

    for move_name in pokemon.moves:
        move_data = pokemon.get_move_data(move_name)
        if not move_data:
            continue
        power = move_data["power"]
        if move_data["category"] == "physical":
            atk_stat = pokemon.atk
            def_stat = opponent.defense
        else:
            atk_stat = pokemon.spa
            def_stat = opponent.spd

        base = ((2 * pokemon.level / 5 + 2) * power * atk_stat / def_stat) / 50 + 2
        type_mult = get_type_multiplier(move_data["type"], opponent.types)
        stab = 1.5 if move_data["type"] in pokemon.types else 1.0
        score = base * type_mult * stab * (move_data["accuracy"] / 100.0)

        if score > best_score:
            best_score = score
            best_move = move_name

    return best_move if best_move else pokemon.moves[0]


def execute_move(attacker, defender, move_name):
    """
    Execute a move. Returns list of event dicts:
    {"type": "use_move", "user": species, "move": name}
    {"type": "miss"}
    {"type": "immune", "target": species}
    {"type": "effective", "multiplier": float}
    {"type": "damage", "target": species, "damage": int, "hp": int, "max_hp": int}
    {"type": "faint", "target": species}
    """
    events = []
    move_data = attacker.get_move_data(move_name)
    if not move_data:
        events.append({"type": "fail", "user": attacker.species, "move": move_name})
        return events

    events.append({"type": "use_move", "user": attacker.species, "move": move_name,
                    "move_type": move_data["type"]})

    # Accuracy check
    if random.randint(1, 100) > move_data["accuracy"]:
        events.append({"type": "miss"})
        return events

    damage, type_mult = calc_damage(attacker, defender, move_data)

    if type_mult == 0:
        events.append({"type": "immune", "target": defender.species})
        return events

    if type_mult >= 2.0:
        events.append({"type": "effective", "multiplier": type_mult})
    elif type_mult <= 0.5:
        events.append({"type": "effective", "multiplier": type_mult})

    defender.current_hp = max(0, defender.current_hp - damage)

    events.append({
        "type": "damage", "target": defender.species,
        "damage": damage, "hp": defender.current_hp, "max_hp": defender.max_hp,
    })

    if defender.is_fainted():
        events.append({"type": "faint", "target": defender.species})

    return events
