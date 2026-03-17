"""
Pokemon League Champion - Battle Logic (pure, no UI)
Full battle engine ported from PokemonBattleEngine (C#).
All functions return event-dict lists for UI consumption.
"""
import random
from data import MOVES_DB, get_type_multiplier, ITEMS, TYPE_BOOSTING_ITEMS, ITEM_TYPE_BOOST
from enums import (
    Status1, Status2, Weather, TeamStatus, BattleStatus,
    MoveCategory, MoveEffect, MoveFlag,
    MAX_STAT_CHANGE, CRIT_MULTIPLIER,
    BURN_DAMAGE_DIVISOR, POISON_DAMAGE_DIVISOR, LEECH_SEED_DIVISOR,
    HAIL_DAMAGE_DIVISOR, SANDSTORM_DAMAGE_DIVISOR, TOXIC_DAMAGE_DIVISOR,
    WEATHER_DURATION, REFLECT_TURNS, LIGHT_SCREEN_TURNS, TAILWIND_TURNS,
    TRICK_ROOM_TURNS, SPIKES_MAX, TOXIC_SPIKES_MAX,
    SLEEP_MIN_TURNS, SLEEP_MAX_TURNS, CONFUSION_MIN_TURNS, CONFUSION_MAX_TURNS,
)


# =====================================================================
#  Battlefield state  (one per battle)
# =====================================================================
class BattleState:
    """Tracks weather, team-side hazards/screens, and global flags."""
    def __init__(self):
        self.weather = Weather.NONE
        self.weather_turns = 0
        self.battle_status = BattleStatus(0)

        # Per-side team status  (index 0 = player, 1 = enemy)
        self.team_status = [TeamStatus(0), TeamStatus(0)]
        self.screen_turns = [{}, {}]       # e.g. {TeamStatus.REFLECT: 3}
        self.spikes_count = [0, 0]         # 0–3
        self.toxic_spikes_count = [0, 0]   # 0–2
        self.tailwind_turns = [0, 0]
        self.wish_hp = [0, 0]  # pending Wish heal


# =====================================================================
#  Stat & multiplier helpers
# =====================================================================
def _stat_stage_mult(stage, for_accuracy=False):
    base = 3 if for_accuracy else 2
    if stage >= 0:
        return (base + stage) / base
    return base / (base - stage)


def _get_attack_stat(attacker, move_data, crit, state):
    """Get effective attack stat for damage formula."""
    cat = move_data["category"]
    if cat == "physical":
        raw = attacker.atk
        stage = attacker.stat_changes["atk"]
    else:
        raw = attacker.spa
        stage = attacker.stat_changes["spa"]

    # Crits ignore negative stat changes on the attacker
    if crit and stage < 0:
        stage = 0
    value = max(1, int(raw * _stat_stage_mult(stage)))

    # Ability modifiers
    ab = attacker.ability
    if ab == "Huge Power" or ab == "Pure Power":
        if cat == "physical":
            value = int(value * 2)
    if ab == "Hustle" and cat == "physical":
        value = int(value * 1.5)
    if ab == "Guts" and attacker.has_status1() and cat == "physical":
        value = int(value * 1.5)
    if ab == "Overgrow" and move_data["type"] == "Grass" and attacker.current_hp <= attacker.max_hp // 3:
        value = int(value * 1.5)
    if ab == "Blaze" and move_data["type"] == "Fire" and attacker.current_hp <= attacker.max_hp // 3:
        value = int(value * 1.5)
    if ab == "Torrent" and move_data["type"] == "Water" and attacker.current_hp <= attacker.max_hp // 3:
        value = int(value * 1.5)
    if ab == "Swarm" and move_data["type"] == "Bug" and attacker.current_hp <= attacker.max_hp // 3:
        value = int(value * 1.5)
    if ab == "Solar Power" and cat == "special" and state.weather == Weather.HARSH_SUNLIGHT:
        value = int(value * 1.5)
    if ab == "Flower Gift" and cat == "physical" and state.weather == Weather.HARSH_SUNLIGHT:
        value = int(value * 1.5)
    if ab == "Slow Start" and attacker.slow_start_turns < 5 and cat == "physical":
        value = int(value * 0.5)
    if ab == "Defeatist" and attacker.current_hp <= attacker.max_hp // 2:
        value = int(value * 0.5)
    if ab == "Flash Fire" and attacker.flash_fire_activated and move_data["type"] == "Fire":
        value = int(value * 1.5)
    if ab == "Toxic Boost" and attacker.status1 in (Status1.POISONED, Status1.BADLY_POISONED) and cat == "physical":
        value = int(value * 1.5)

    # Item modifiers
    item = attacker.item
    if item == "Choice Band" and cat == "physical":
        value = int(value * 1.5)
    if item == "Choice Specs" and cat == "special":
        value = int(value * 1.5)
    if item == "Life Orb":
        value = int(value * 1.3)
    # Type-boosting items
    boost_type = ITEM_TYPE_BOOST.get(item)
    if boost_type and boost_type == move_data["type"]:
        value = int(value * 1.2)

    return max(1, value)


def _get_defense_stat(defender, move_data, crit, state):
    """Get effective defense stat for damage formula."""
    cat = move_data["category"]
    effect = move_data.get("effect", MoveEffect.HIT)

    # Psyshock hits physical defense with special category
    if effect == MoveEffect.PSYSHOCK_EFFECT:
        raw = defender.defense
        stage = defender.stat_changes["def"]
    elif cat == "physical":
        raw = defender.defense
        stage = defender.stat_changes["def"]
    else:
        raw = defender.spd
        stage = defender.stat_changes["spd"]

    # Crits ignore positive stat changes on the defender
    if crit and stage > 0:
        stage = 0
    value = max(1, int(raw * _stat_stage_mult(stage)))

    # Ability modifiers on defender
    ab = defender.ability
    if ab == "Marvel Scale" and defender.has_status1() and cat == "physical":
        value = int(value * 1.5)
    if ab == "Flower Gift" and cat == "special" and state.weather == Weather.HARSH_SUNLIGHT:
        value = int(value * 1.5)

    # Sand: Rock types get +50% SpDef
    if state.weather == Weather.SANDSTORM and "Rock" in defender.types and cat == "special":
        value = int(value * 1.5)

    # Item modifiers
    if defender.item == "Assault Vest" and cat == "special":
        value = int(value * 1.5)
    if defender.item == "Eviolite":
        value = int(value * 1.5)

    return max(1, value)


def _calc_base_power(attacker, defender, move_name, move_data, state):
    """Calculate effective base power with ability/weather adjustments."""
    power = move_data["power"]
    if power == 0:
        return 0

    effect = move_data.get("effect", MoveEffect.HIT)
    mtype = move_data["type"]

    # Eruption: power scales with HP
    if effect == MoveEffect.ERUPTION:
        power = max(1, int(150 * attacker.current_hp / attacker.max_hp))

    # Facade doubles vs status
    if effect == MoveEffect.FACADE and attacker.has_status1():
        power *= 2

    # Venoshock doubles vs poisoned target
    if effect == MoveEffect.VENOSHOCK and defender.status1 in (Status1.POISONED, Status1.BADLY_POISONED):
        power *= 2

    # Hex doubles vs status
    if effect == MoveEffect.HEX_EFFECT and defender.has_status1():
        power *= 2

    # Weather-boosted moves
    if state.weather == Weather.HARSH_SUNLIGHT:
        if mtype == "Fire":
            power = int(power * 1.5)
        elif mtype == "Water":
            power = int(power * 0.5)
    elif state.weather == Weather.RAIN:
        if mtype == "Water":
            power = int(power * 1.5)
        elif mtype == "Fire":
            power = int(power * 0.5)

    # Technician
    if attacker.ability == "Technician" and power <= 60:
        power = int(power * 1.5)

    # Reckless: boosts recoil moves
    if attacker.ability == "Reckless" and effect == MoveEffect.RECOIL:
        power = int(power * 1.2)

    # Iron Fist: boosts punching moves
    flags = move_data.get("flags", MoveFlag.NONE)
    if attacker.ability == "Iron Fist" and (flags & MoveFlag.PUNCHING):
        power = int(power * 1.2)

    # Strong Jaw: boosts biting moves
    if attacker.ability == "Strong Jaw" and (flags & MoveFlag.BITING):
        power = int(power * 1.5)

    # Sheer Force: boosts moves with secondary effects, removes the effect
    if attacker.ability == "Sheer Force" and move_data.get("effect_chance", 0) > 0:
        power = int(power * 1.3)

    # Adaptability: STAB becomes 2.0 instead of 1.5 (handled in damage multiplier)

    return max(1, power)


# =====================================================================
#  Critical hit check
# =====================================================================
def _crit_check(attacker, move_data):
    """Returns True if the hit is a critical."""
    stage = 0
    flags = move_data.get("flags", MoveFlag.NONE)
    if flags & MoveFlag.HIGH_CRIT:
        stage += 1
    if attacker.ability == "Super Luck":
        stage += 1
    if attacker.has_status2(Status2.PUMPED):  # Focus Energy
        stage += 2
    if attacker.item == "Scope Lens":
        stage += 1

    rates = [16, 8, 4, 3, 2]
    idx = min(stage, len(rates) - 1)
    return random.randint(1, rates[idx]) == 1


# =====================================================================
#  Accuracy / miss check
# =====================================================================
def _accuracy_check(attacker, defender, move_data, state):
    """Returns True if the move hits."""
    acc = move_data["accuracy"]
    if acc == 0:  # Never-miss moves (Aerial Ace, Aura Sphere, etc.)
        return True

    # No Guard: both sides always hit
    if attacker.ability == "No Guard" or defender.ability == "No Guard":
        return True

    # Calculate accuracy with stat stages
    acc_stage = attacker.stat_changes.get("acc", 0)
    eva_stage = defender.stat_changes.get("eva", 0)

    # Abilities
    if attacker.ability == "Compound Eyes":
        acc = int(acc * 1.3)
    if attacker.ability == "Hustle" and move_data["category"] == "physical":
        acc = int(acc * 0.8)
    if defender.ability == "Sand Veil" and state.weather == Weather.SANDSTORM:
        acc = int(acc * 0.8)
    if defender.ability == "Snow Cloak" and state.weather == Weather.HAILSTORM:
        acc = int(acc * 0.8)
    if defender.ability == "Tangled Feet" and defender.has_status2(Status2.CONFUSED):
        eva_stage += 1

    # Items
    if attacker.item == "Wide Lens":
        acc = int(acc * 1.1)
    if defender.item == "Bright Powder":
        acc = int(acc * 0.9)

    # Apply stat stages
    effective_acc = int(acc * _stat_stage_mult(acc_stage, True) / _stat_stage_mult(eva_stage, True))

    return random.randint(1, 100) <= effective_acc


# =====================================================================
#  Main damage calculation  (ported from PBE BattleDamage.cs)
# =====================================================================
def calc_damage(attacker, defender, move_name, move_data, state, crit=False):
    """Full damage calculation. Returns (damage, type_multiplier, is_crit)."""
    base_power = _calc_base_power(attacker, defender, move_name, move_data, state)
    if base_power == 0:
        return 0, 1.0, False

    level = attacker.level
    atk_stat = _get_attack_stat(attacker, move_data, crit, state)
    def_stat = _get_defense_stat(defender, move_data, crit, state)

    # Core formula: ((2*level/5+2) * power * atk / def / 50 + 2)
    damage = int(((2 * level / 5 + 2) * base_power * atk_stat / def_stat) / 50 + 2)

    # Random factor 85-100%
    damage = int(damage * random.randint(85, 100) / 100)

    # STAB
    if move_data["type"] in attacker.types:
        if attacker.ability == "Adaptability":
            damage = int(damage * 2.0)
        else:
            damage = int(damage * 1.5)

    # Type effectiveness
    type_mult = get_type_multiplier(move_data["type"], defender.types)

    # Abilities that modify type effectiveness
    if type_mult > 1.0 and defender.ability == "Solid Rock":
        type_mult *= 0.75
    if type_mult > 1.0 and defender.ability == "Filter":
        type_mult *= 0.75
    if move_data["type"] == "Ground" and not defender.is_grounded() and defender.ability != "Levitate":
        pass  # already handled by type chart for Flying
    if move_data["type"] == "Ground" and defender.ability == "Levitate" and type_mult > 0:
        type_mult = 0

    # Tinted Lens: not very effective moves do normal damage
    if attacker.ability == "Tinted Lens" and 0 < type_mult < 1:
        type_mult *= 2

    damage = int(damage * type_mult)

    # Critical hit multiplier
    if crit:
        damage = int(damage * CRIT_MULTIPLIER)

    # Burn halves physical damage (Guts users immune)
    if (attacker.status1 == Status1.BURNED
            and move_data["category"] == "physical"
            and attacker.ability != "Guts"):
        damage = int(damage * 0.5)

    # Screens
    side = 1  # defender is enemy by default; caller should set this
    if not crit:
        if move_data["category"] == "physical" and (state.team_status[1] & TeamStatus.REFLECT):
            damage = int(damage * 0.5)
        if move_data["category"] == "special" and (state.team_status[1] & TeamStatus.LIGHT_SCREEN):
            damage = int(damage * 0.5)

    # Sniper ability
    if crit and attacker.ability == "Sniper":
        damage = int(damage * 1.5)

    # Multiscale: full HP halves damage
    if defender.ability == "Multiscale" and defender.current_hp == defender.max_hp:
        damage = int(damage * 0.5)

    # Sturdy: survive at 1 HP from full
    if (defender.ability == "Sturdy" and defender.current_hp == defender.max_hp
            and damage >= defender.current_hp):
        damage = defender.current_hp - 1

    # Focus Sash: survive at 1 HP from full
    if (defender.item == "Focus Sash" and defender.current_hp == defender.max_hp
            and damage >= defender.current_hp):
        damage = defender.current_hp - 1
        defender.item = None  # consumed

    return max(1, damage) if type_mult > 0 else 0, type_mult, crit


# =====================================================================
#  Pre-move status checks  (sleep, freeze, para, confuse, flinch, infatuation)
# =====================================================================
def _pre_move_status_check(attacker, events):
    """Check if attacker can act. Returns False if they can't move."""
    # --- Sleep ---
    if attacker.status1 == Status1.ASLEEP:
        attacker.sleep_counter += 1
        if attacker.sleep_counter >= attacker.sleep_turns:
            attacker.status1 = Status1.NONE
            events.append({"type": "status_cure", "target": attacker.species, "status": "sleep"})
        else:
            events.append({"type": "status_immobile", "target": attacker.species, "status": "sleep"})
            return False

    # --- Freeze ---
    if attacker.status1 == Status1.FROZEN:
        if random.randint(1, 5) == 1:  # 20% thaw
            attacker.status1 = Status1.NONE
            events.append({"type": "status_cure", "target": attacker.species, "status": "freeze"})
        else:
            events.append({"type": "status_immobile", "target": attacker.species, "status": "freeze"})
            return False

    # --- Flinch ---
    if attacker.has_status2(Status2.FLINCHING):
        attacker.clear_status2(Status2.FLINCHING)
        events.append({"type": "status_immobile", "target": attacker.species, "status": "flinch"})
        if attacker.ability == "Steadfast":
            actual = attacker.change_stat("spe", 1)
            if actual:
                events.append({"type": "stat_change", "target": attacker.species, "stat": "Speed", "amount": 1})
        return False

    # --- Confusion ---
    if attacker.has_status2(Status2.CONFUSED):
        attacker.confusion_counter += 1
        if attacker.confusion_counter >= attacker.confusion_turns:
            attacker.clear_status2(Status2.CONFUSED)
            events.append({"type": "status_cure", "target": attacker.species, "status": "confusion"})
        elif random.randint(1, 2) == 1:  # 50% chance to hit self
            # Self-hit: 40 power typeless physical
            raw = attacker.atk
            stage = attacker.stat_changes["atk"]
            a = max(1, int(raw * _stat_stage_mult(stage)))
            d = max(1, int(attacker.defense * _stat_stage_mult(attacker.stat_changes["def"])))
            dmg = int(((2 * attacker.level / 5 + 2) * 40 * a / d) / 50 + 2)
            attacker.current_hp = max(0, attacker.current_hp - dmg)
            events.append({"type": "confusion_hit", "target": attacker.species, "damage": dmg,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
            if attacker.is_fainted():
                events.append({"type": "faint", "target": attacker.species})
            return False

    # --- Paralysis ---
    if attacker.status1 == Status1.PARALYZED:
        if random.randint(1, 4) == 1:  # 25% fully paralyzed
            events.append({"type": "status_immobile", "target": attacker.species, "status": "paralysis"})
            return False

    # --- Infatuation ---
    if attacker.has_status2(Status2.INFATUATED):
        if random.randint(1, 2) == 1:
            events.append({"type": "status_immobile", "target": attacker.species, "status": "infatuation"})
            return False

    return True  # can act


# =====================================================================
#  Apply secondary effects
# =====================================================================
def _apply_secondary_effect(attacker, defender, move_data, events, state):
    """Apply secondary effects (burn chance, stat drops, etc.)."""
    effect = move_data.get("effect", MoveEffect.HIT)
    chance = move_data.get("effect_chance", 0)

    # Sheer Force: no secondary effects
    if attacker.ability == "Sheer Force" and chance > 0:
        return

    # Serene Grace doubles effect chance
    if attacker.ability == "Serene Grace":
        chance = min(100, chance * 2)

    if chance > 0 and random.randint(1, 100) > chance:
        return  # didn't trigger

    # --- Status infliction effects ---
    if effect == MoveEffect.HIT_MAYBE_BURN:
        if defender.can_be_burned():
            defender.status1 = Status1.BURNED
            events.append({"type": "status_inflict", "target": defender.species, "status": "burn"})

    elif effect == MoveEffect.HIT_MAYBE_FREEZE:
        if defender.can_be_frozen():
            defender.status1 = Status1.FROZEN
            events.append({"type": "status_inflict", "target": defender.species, "status": "freeze"})

    elif effect == MoveEffect.HIT_MAYBE_PARALYZE:
        if defender.can_be_paralyzed():
            defender.status1 = Status1.PARALYZED
            events.append({"type": "status_inflict", "target": defender.species, "status": "paralysis"})

    elif effect == MoveEffect.HIT_MAYBE_POISON:
        if defender.can_be_poisoned():
            defender.status1 = Status1.POISONED
            events.append({"type": "status_inflict", "target": defender.species, "status": "poison"})

    elif effect == MoveEffect.HIT_MAYBE_CONFUSE:
        if not defender.has_status2(Status2.CONFUSED):
            defender.set_status2(Status2.CONFUSED)
            defender.confusion_turns = random.randint(2, 5)
            defender.confusion_counter = 0
            events.append({"type": "status_inflict", "target": defender.species, "status": "confusion"})

    elif effect == MoveEffect.HIT_MAYBE_FLINCH:
        if not defender.has_status2(Status2.FLINCHING):
            defender.set_status2(Status2.FLINCHING)

    # --- Stat change effects ---
    elif effect == MoveEffect.HIT_MAYBE_LOWER_TARGET_DEF:
        actual = defender.change_stat("def", -1)
        if actual:
            events.append({"type": "stat_change", "target": defender.species, "stat": "Defense", "amount": -1})

    elif effect == MoveEffect.HIT_MAYBE_LOWER_TARGET_SPDEF:
        actual = defender.change_stat("spd", -1)
        if actual:
            events.append({"type": "stat_change", "target": defender.species, "stat": "Sp.Def", "amount": -1})

    elif effect == MoveEffect.HIT_MAYBE_LOWER_TARGET_SPATK:
        actual = defender.change_stat("spa", -1)
        if actual:
            events.append({"type": "stat_change", "target": defender.species, "stat": "Sp.Atk", "amount": -1})

    elif effect == MoveEffect.HIT_MAYBE_LOWER_TARGET_ACC:
        actual = defender.change_stat("acc", -1)
        if actual:
            events.append({"type": "stat_change", "target": defender.species, "stat": "Accuracy", "amount": -1})

    elif effect == MoveEffect.HIT_MAYBE_RAISE_USER_ATK:
        actual = attacker.change_stat("atk", 1)
        if actual:
            events.append({"type": "stat_change", "target": attacker.species, "stat": "Attack", "amount": 1})


# =====================================================================
#  Status-only move execution
# =====================================================================
def _execute_status_move(attacker, defender, move_name, move_data, events, state, attacker_side):
    """Execute a status-category move. Returns events."""
    effect = move_data.get("effect", MoveEffect.HIT)
    defender_side = 1 - attacker_side

    if effect == MoveEffect.BURN:
        if defender.can_be_burned():
            defender.status1 = Status1.BURNED
            events.append({"type": "status_inflict", "target": defender.species, "status": "burn"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.PARALYZE:
        if defender.can_be_paralyzed():
            defender.status1 = Status1.PARALYZED
            events.append({"type": "status_inflict", "target": defender.species, "status": "paralysis"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.TOXIC:
        if defender.can_be_poisoned():
            defender.status1 = Status1.BADLY_POISONED
            defender.badly_poisoned_counter = 0
            events.append({"type": "status_inflict", "target": defender.species, "status": "bad poison"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.SLEEP:
        if defender.can_be_put_to_sleep():
            defender.status1 = Status1.ASLEEP
            defender.sleep_turns = random.randint(1, 3)
            defender.sleep_counter = 0
            events.append({"type": "status_inflict", "target": defender.species, "status": "sleep"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.CONFUSE:
        if not defender.has_status2(Status2.CONFUSED):
            defender.set_status2(Status2.CONFUSED)
            defender.confusion_turns = random.randint(2, 5)
            defender.confusion_counter = 0
            events.append({"type": "status_inflict", "target": defender.species, "status": "confusion"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.PROTECT:
        if attacker.protect_counter > 0 and random.randint(1, 2**attacker.protect_counter) != 1:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            attacker.set_status2(Status2.PROTECTED)
            attacker.protect_counter += 1
            events.append({"type": "protect", "target": attacker.species})

    elif effect == MoveEffect.HEAL:
        heal_amount = attacker.max_hp // 2
        actual = attacker.heal(heal_amount)
        if actual > 0:
            events.append({"type": "heal", "target": attacker.species, "amount": actual,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.REST:
        if attacker.current_hp < attacker.max_hp:
            attacker.current_hp = attacker.max_hp
            attacker.status1 = Status1.ASLEEP
            attacker.sleep_turns = 3
            attacker.sleep_counter = 0
            events.append({"type": "heal", "target": attacker.species, "amount": attacker.max_hp,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
            events.append({"type": "status_inflict", "target": attacker.species, "status": "sleep"})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.SUBSTITUTE_EFFECT:
        cost = attacker.max_hp // 4
        if attacker.current_hp > cost and attacker.substitute_hp == 0:
            attacker.current_hp -= cost
            attacker.substitute_hp = cost
            events.append({"type": "substitute", "target": attacker.species, "hp_cost": cost})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.LEECH_SEED_EFFECT:
        if "Grass" in defender.types or defender.has_status2(Status2.LEECH_SEED):
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            defender.set_status2(Status2.LEECH_SEED)
            events.append({"type": "status_inflict", "target": defender.species, "status": "leech seed"})

    elif effect == MoveEffect.STEALTH_ROCK_EFFECT:
        if state.team_status[defender_side] & TeamStatus.STEALTH_ROCK:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.team_status[defender_side] = TeamStatus(state.team_status[defender_side] | TeamStatus.STEALTH_ROCK)
            events.append({"type": "hazard_set", "side": defender_side, "hazard": "Stealth Rock"})

    elif effect == MoveEffect.SPIKES_EFFECT:
        if state.spikes_count[defender_side] >= 3:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.spikes_count[defender_side] += 1
            state.team_status[defender_side] = TeamStatus(state.team_status[defender_side] | TeamStatus.SPIKES)
            events.append({"type": "hazard_set", "side": defender_side, "hazard": "Spikes"})

    elif effect == MoveEffect.TOXIC_SPIKES_EFFECT:
        if state.toxic_spikes_count[defender_side] >= 2:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.toxic_spikes_count[defender_side] += 1
            state.team_status[defender_side] = TeamStatus(state.team_status[defender_side] | TeamStatus.TOXIC_SPIKES)
            events.append({"type": "hazard_set", "side": defender_side, "hazard": "Toxic Spikes"})

    elif effect == MoveEffect.REFLECT_EFFECT:
        if state.team_status[attacker_side] & TeamStatus.REFLECT:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.team_status[attacker_side] = TeamStatus(state.team_status[attacker_side] | TeamStatus.REFLECT)
            state.screen_turns[attacker_side][TeamStatus.REFLECT] = REFLECT_TURNS
            events.append({"type": "screen_set", "side": attacker_side, "screen": "Reflect"})

    elif effect == MoveEffect.LIGHT_SCREEN_EFFECT:
        if state.team_status[attacker_side] & TeamStatus.LIGHT_SCREEN:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.team_status[attacker_side] = TeamStatus(state.team_status[attacker_side] | TeamStatus.LIGHT_SCREEN)
            state.screen_turns[attacker_side][TeamStatus.LIGHT_SCREEN] = LIGHT_SCREEN_TURNS
            events.append({"type": "screen_set", "side": attacker_side, "screen": "Light Screen"})

    elif effect == MoveEffect.TAILWIND_EFFECT:
        if state.tailwind_turns[attacker_side] > 0:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            state.tailwind_turns[attacker_side] = TAILWIND_TURNS
            events.append({"type": "tailwind", "side": attacker_side})

    elif effect == MoveEffect.SUNNY_DAY:
        state.weather = Weather.HARSH_SUNLIGHT
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Harsh Sunlight"})

    elif effect == MoveEffect.RAIN_DANCE:
        state.weather = Weather.RAIN
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Rain"})

    elif effect == MoveEffect.HAIL:
        state.weather = Weather.HAILSTORM
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Hail"})

    elif effect == MoveEffect.TRICK_ROOM_EFFECT:
        if state.battle_status & BattleStatus.TRICK_ROOM:
            state.battle_status = BattleStatus(state.battle_status & ~BattleStatus.TRICK_ROOM)
            events.append({"type": "field_end", "effect": "Trick Room"})
        else:
            state.battle_status = BattleStatus(state.battle_status | BattleStatus.TRICK_ROOM)
            events.append({"type": "field_set", "effect": "Trick Room"})

    elif effect == MoveEffect.FOCUS_ENERGY:
        if attacker.has_status2(Status2.PUMPED):
            events.append({"type": "fail", "user": attacker.species, "move": move_name})
        else:
            attacker.set_status2(Status2.PUMPED)
            events.append({"type": "status_inflict", "target": attacker.species, "status": "pumped up"})

    elif effect == MoveEffect.HAZE:
        attacker.clear_stat_changes()
        defender.clear_stat_changes()
        events.append({"type": "haze"})

    elif effect == MoveEffect.BELLY_DRUM:
        half = attacker.max_hp // 2
        if attacker.current_hp > half and attacker.stat_changes["atk"] < 6:
            attacker.current_hp -= half
            attacker.stat_changes["atk"] = 6
            events.append({"type": "belly_drum", "target": attacker.species,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})

    elif effect == MoveEffect.CURSE:
        if "Ghost" in attacker.types:
            # Ghost Curse: sacrifice HP, curse target
            cost = attacker.max_hp // 2
            attacker.current_hp = max(0, attacker.current_hp - cost)
            defender.set_status2(Status2.CURSED)
            events.append({"type": "curse_ghost", "user": attacker.species, "target": defender.species,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
            if attacker.is_fainted():
                events.append({"type": "faint", "target": attacker.species})
        else:
            # Non-ghost Curse: +1 Atk, +1 Def, -1 Spe
            a1 = attacker.change_stat("atk", 1)
            a2 = attacker.change_stat("def", 1)
            a3 = attacker.change_stat("spe", -1)
            if a1:
                events.append({"type": "stat_change", "target": attacker.species, "stat": "Attack", "amount": 1})
            if a2:
                events.append({"type": "stat_change", "target": attacker.species, "stat": "Defense", "amount": 1})
            if a3:
                events.append({"type": "stat_change", "target": attacker.species, "stat": "Speed", "amount": -1})

    elif effect in (MoveEffect.CHANGE_TARGET_ATK, MoveEffect.CHANGE_TARGET_SPATK):
        param = move_data.get("effect_param", 1)
        # These are self-targeting stat boosts
        if effect == MoveEffect.CHANGE_TARGET_ATK:
            stat_key, stat_name = "atk", "Attack"
            # Dragon Dance: also +1 Spe
            if move_name == "Dragon Dance":
                a1 = attacker.change_stat("atk", param)
                a2 = attacker.change_stat("spe", param)
                if a1:
                    events.append({"type": "stat_change", "target": attacker.species, "stat": "Attack", "amount": param})
                if a2:
                    events.append({"type": "stat_change", "target": attacker.species, "stat": "Speed", "amount": param})
                return
            # Shell Smash: +2 Atk, +2 SpA, +2 Spe, -1 Def, -1 SpD
            if move_name == "Shell Smash":
                for s, n in [("atk", "Attack"), ("spa", "Sp.Atk"), ("spe", "Speed")]:
                    a = attacker.change_stat(s, 2)
                    if a:
                        events.append({"type": "stat_change", "target": attacker.species, "stat": n, "amount": 2})
                for s, n in [("def", "Defense"), ("spd", "Sp.Def")]:
                    a = attacker.change_stat(s, -1)
                    if a:
                        events.append({"type": "stat_change", "target": attacker.species, "stat": n, "amount": -1})
                return
        else:
            stat_key, stat_name = "spa", "Sp.Atk"
            # Calm Mind: +1 SpA, +1 SpD
            if move_name == "Calm Mind":
                a1 = attacker.change_stat("spa", param)
                a2 = attacker.change_stat("spd", param)
                if a1:
                    events.append({"type": "stat_change", "target": attacker.species, "stat": "Sp.Atk", "amount": param})
                if a2:
                    events.append({"type": "stat_change", "target": attacker.species, "stat": "Sp.Def", "amount": param})
                return

        actual = attacker.change_stat(stat_key, param)
        if actual:
            events.append({"type": "stat_change", "target": attacker.species, "stat": stat_name, "amount": param})
        else:
            events.append({"type": "fail", "user": attacker.species, "move": move_name})


# =====================================================================
#  Switch-in effects (entry hazards)
# =====================================================================
def do_switch_in_effects(pokemon, side, state):
    """Apply entry hazards when a Pokemon switches in. Returns event list."""
    events = []

    # Stealth Rock: damage based on type effectiveness to Rock
    if state.team_status[side] & TeamStatus.STEALTH_ROCK:
        mult = get_type_multiplier("Rock", pokemon.types)
        dmg = max(1, int(pokemon.max_hp * mult / 8))
        pokemon.current_hp = max(0, pokemon.current_hp - dmg)
        events.append({"type": "hazard_damage", "target": pokemon.species, "hazard": "Stealth Rock",
                       "damage": dmg, "hp": pokemon.current_hp, "max_hp": pokemon.max_hp})
        if pokemon.is_fainted():
            events.append({"type": "faint", "target": pokemon.species})
            return events

    # Spikes: only grounded Pokemon
    if (state.team_status[side] & TeamStatus.SPIKES) and pokemon.is_grounded():
        count = state.spikes_count[side]
        divisors = {1: 8, 2: 6, 3: 4}
        dmg = max(1, pokemon.max_hp // divisors.get(count, 8))
        pokemon.current_hp = max(0, pokemon.current_hp - dmg)
        events.append({"type": "hazard_damage", "target": pokemon.species, "hazard": "Spikes",
                       "damage": dmg, "hp": pokemon.current_hp, "max_hp": pokemon.max_hp})
        if pokemon.is_fainted():
            events.append({"type": "faint", "target": pokemon.species})
            return events

    # Toxic Spikes: poison grounded Pokemon (Poison types absorb them)
    if (state.team_status[side] & TeamStatus.TOXIC_SPIKES) and pokemon.is_grounded():
        if "Poison" in pokemon.types:
            # Grounded Poison type absorbs toxic spikes
            state.toxic_spikes_count[side] = 0
            state.team_status[side] = TeamStatus(state.team_status[side] & ~TeamStatus.TOXIC_SPIKES)
            events.append({"type": "hazard_clear", "target": pokemon.species, "hazard": "Toxic Spikes"})
        elif pokemon.can_be_poisoned():
            count = state.toxic_spikes_count[side]
            if count >= 2:
                pokemon.status1 = Status1.BADLY_POISONED
                pokemon.badly_poisoned_counter = 0
                events.append({"type": "status_inflict", "target": pokemon.species, "status": "bad poison"})
            else:
                pokemon.status1 = Status1.POISONED
                events.append({"type": "status_inflict", "target": pokemon.species, "status": "poison"})

    # Switch-in abilities
    ab = pokemon.ability
    if ab == "Intimidate":
        # Would target enemy - handled by caller
        events.append({"type": "ability_announce", "pokemon": pokemon.species, "ability": "Intimidate"})
    if ab == "Sand Stream":
        state.weather = Weather.SANDSTORM
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Sandstorm"})
    if ab == "Snow Warning":
        state.weather = Weather.HAILSTORM
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Hail"})
    if ab == "Drizzle":
        state.weather = Weather.RAIN
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Rain"})
    if ab == "Drought":
        state.weather = Weather.HARSH_SUNLIGHT
        state.weather_turns = WEATHER_DURATION
        events.append({"type": "weather", "weather": "Harsh Sunlight"})
    if ab == "Slow Start":
        pokemon.slow_start_turns = 0
        events.append({"type": "ability_announce", "pokemon": pokemon.species, "ability": "Slow Start"})

    return events


# =====================================================================
#  Turn-end effects  (weather damage, status damage, Leftovers, etc.)
# =====================================================================
def do_turn_end_effects(player_poke, enemy_poke, state):
    """Process end-of-turn effects for both sides. Returns event list."""
    events = []

    # Weather countdown
    if state.weather != Weather.NONE:
        state.weather_turns -= 1
        if state.weather_turns <= 0:
            events.append({"type": "weather_end", "weather": state.weather.name})
            state.weather = Weather.NONE
        else:
            # Weather damage
            for poke in [player_poke, enemy_poke]:
                if poke.is_fainted():
                    continue
                if state.weather == Weather.SANDSTORM:
                    if not any(t in poke.types for t in ["Rock", "Ground", "Steel"]):
                        if poke.ability not in ("Sand Veil", "Sand Rush", "Sand Force", "Overcoat", "Magic Guard"):
                            dmg = max(1, poke.max_hp // SANDSTORM_DAMAGE_DIVISOR)
                            poke.current_hp = max(0, poke.current_hp - dmg)
                            events.append({"type": "weather_damage", "target": poke.species,
                                           "damage": dmg, "weather": "Sandstorm",
                                           "hp": poke.current_hp, "max_hp": poke.max_hp})
                elif state.weather == Weather.HAILSTORM:
                    if "Ice" not in poke.types:
                        if poke.ability not in ("Snow Cloak", "Ice Body", "Overcoat", "Magic Guard"):
                            dmg = max(1, poke.max_hp // HAIL_DAMAGE_DIVISOR)
                            poke.current_hp = max(0, poke.current_hp - dmg)
                            events.append({"type": "weather_damage", "target": poke.species,
                                           "damage": dmg, "weather": "Hail",
                                           "hp": poke.current_hp, "max_hp": poke.max_hp})
                # Ice Body / Rain Dish healing
                if poke.ability == "Ice Body" and state.weather == Weather.HAILSTORM:
                    healed = poke.heal(poke.max_hp // 16)
                    if healed:
                        events.append({"type": "ability_heal", "target": poke.species,
                                       "ability": "Ice Body", "amount": healed,
                                       "hp": poke.current_hp, "max_hp": poke.max_hp})
                if poke.ability == "Rain Dish" and state.weather == Weather.RAIN:
                    healed = poke.heal(poke.max_hp // 16)
                    if healed:
                        events.append({"type": "ability_heal", "target": poke.species,
                                       "ability": "Rain Dish", "amount": healed,
                                       "hp": poke.current_hp, "max_hp": poke.max_hp})

    # Screen & tailwind countdowns
    for side in [0, 1]:
        for screen in list(state.screen_turns[side]):
            state.screen_turns[side][screen] -= 1
            if state.screen_turns[side][screen] <= 0:
                state.team_status[side] = TeamStatus(state.team_status[side] & ~screen)
                del state.screen_turns[side][screen]
                name = "Reflect" if screen == TeamStatus.REFLECT else "Light Screen"
                events.append({"type": "screen_end", "side": side, "screen": name})
        if state.tailwind_turns[side] > 0:
            state.tailwind_turns[side] -= 1
            if state.tailwind_turns[side] <= 0:
                events.append({"type": "tailwind_end", "side": side})

    # Per-Pokemon end-of-turn effects
    for poke in [player_poke, enemy_poke]:
        if poke.is_fainted():
            continue

        # Leftovers
        if poke.item == "Leftovers":
            healed = poke.heal(poke.max_hp // 16)
            if healed:
                events.append({"type": "item_heal", "target": poke.species, "item": "Leftovers",
                               "amount": healed, "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Black Sludge
        if poke.item == "Black Sludge":
            if "Poison" in poke.types:
                healed = poke.heal(poke.max_hp // 16)
                if healed:
                    events.append({"type": "item_heal", "target": poke.species, "item": "Black Sludge",
                                   "amount": healed, "hp": poke.current_hp, "max_hp": poke.max_hp})
            else:
                dmg = max(1, poke.max_hp // 8)
                poke.current_hp = max(0, poke.current_hp - dmg)
                events.append({"type": "item_damage", "target": poke.species, "item": "Black Sludge",
                               "damage": dmg, "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Burn damage
        if poke.status1 == Status1.BURNED:
            if poke.ability != "Magic Guard":
                dmg = max(1, poke.max_hp // BURN_DAMAGE_DIVISOR)
                poke.current_hp = max(0, poke.current_hp - dmg)
                events.append({"type": "status_damage", "target": poke.species, "status": "burn",
                               "damage": dmg, "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Poison damage
        if poke.status1 == Status1.POISONED:
            if poke.ability == "Poison Heal":
                healed = poke.heal(poke.max_hp // 8)
                if healed:
                    events.append({"type": "ability_heal", "target": poke.species,
                                   "ability": "Poison Heal", "amount": healed,
                                   "hp": poke.current_hp, "max_hp": poke.max_hp})
            elif poke.ability != "Magic Guard":
                dmg = max(1, poke.max_hp // POISON_DAMAGE_DIVISOR)
                poke.current_hp = max(0, poke.current_hp - dmg)
                events.append({"type": "status_damage", "target": poke.species, "status": "poison",
                               "damage": dmg, "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Badly poisoned damage (escalating)
        if poke.status1 == Status1.BADLY_POISONED:
            poke.badly_poisoned_counter += 1
            if poke.ability == "Poison Heal":
                healed = poke.heal(poke.max_hp // 8)
                if healed:
                    events.append({"type": "ability_heal", "target": poke.species,
                                   "ability": "Poison Heal", "amount": healed,
                                   "hp": poke.current_hp, "max_hp": poke.max_hp})
            elif poke.ability != "Magic Guard":
                dmg = max(1, poke.max_hp * poke.badly_poisoned_counter // 16)
                poke.current_hp = max(0, poke.current_hp - dmg)
                events.append({"type": "status_damage", "target": poke.species, "status": "bad poison",
                               "damage": dmg, "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Leech Seed
        if poke.has_status2(Status2.LEECH_SEED) and poke.ability != "Magic Guard":
            dmg = max(1, poke.max_hp // LEECH_SEED_DIVISOR)
            poke.current_hp = max(0, poke.current_hp - dmg)
            # Heal the other Pokemon
            other = enemy_poke if poke is player_poke else player_poke
            if not other.is_fainted():
                healed = other.heal(dmg)
            events.append({"type": "leech_seed", "target": poke.species, "damage": dmg,
                           "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Curse (ghost)
        if poke.has_status2(Status2.CURSED):
            dmg = max(1, poke.max_hp // 4)
            poke.current_hp = max(0, poke.current_hp - dmg)
            events.append({"type": "curse_damage", "target": poke.species, "damage": dmg,
                           "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Nightmare
        if poke.has_status2(Status2.NIGHTMARE) and poke.status1 == Status1.ASLEEP:
            dmg = max(1, poke.max_hp // 4)
            poke.current_hp = max(0, poke.current_hp - dmg)
            events.append({"type": "nightmare_damage", "target": poke.species, "damage": dmg,
                           "hp": poke.current_hp, "max_hp": poke.max_hp})

        # Speed Boost
        if poke.ability == "Speed Boost" and poke.speed_boost_count > 0:
            actual = poke.change_stat("spe", 1)
            if actual:
                events.append({"type": "ability_stat", "target": poke.species,
                               "ability": "Speed Boost", "stat": "Speed", "amount": 1})
        if poke.ability == "Speed Boost":
            poke.speed_boost_count += 1

        # Slow Start countdown
        if poke.ability == "Slow Start" and poke.slow_start_turns < 5:
            poke.slow_start_turns += 1
            if poke.slow_start_turns >= 5:
                events.append({"type": "ability_end", "target": poke.species, "ability": "Slow Start"})

        # Shed Skin: 30% chance to cure status
        if poke.ability == "Shed Skin" and poke.has_status1():
            if random.randint(1, 100) <= 30:
                old = poke.status1.name.lower()
                poke.status1 = Status1.NONE
                events.append({"type": "ability_cure", "target": poke.species,
                               "ability": "Shed Skin", "status": old})

        if poke.is_fainted():
            events.append({"type": "faint", "target": poke.species})

        # Clear volatile turn-only flags
        poke.clear_status2(Status2.FLINCHING)
        poke.clear_status2(Status2.PROTECTED)

    return events


# =====================================================================
#  Rapid Spin: clear hazards on own side
# =====================================================================
def _rapid_spin_clear(attacker_side, state, events, attacker):
    """Clear hazards and binding on the attacker's side."""
    side = attacker_side
    cleared = False
    if state.team_status[side] & TeamStatus.STEALTH_ROCK:
        state.team_status[side] = TeamStatus(state.team_status[side] & ~TeamStatus.STEALTH_ROCK)
        cleared = True
    if state.team_status[side] & TeamStatus.SPIKES:
        state.team_status[side] = TeamStatus(state.team_status[side] & ~TeamStatus.SPIKES)
        state.spikes_count[side] = 0
        cleared = True
    if state.team_status[side] & TeamStatus.TOXIC_SPIKES:
        state.team_status[side] = TeamStatus(state.team_status[side] & ~TeamStatus.TOXIC_SPIKES)
        state.toxic_spikes_count[side] = 0
        cleared = True
    if cleared:
        events.append({"type": "hazard_clear", "target": attacker.species, "hazard": "all"})


# =====================================================================
#  AI move selection
# =====================================================================
def ai_choose_move(pokemon, opponent, state=None):
    """AI: pick the best move considering full mechanics."""
    if state is None:
        state = BattleState()

    best_move = None
    best_score = -999

    for move_name in pokemon.moves:
        move_data = pokemon.get_move_data(move_name)
        if not move_data:
            continue

        cat = move_data["category"]
        effect = move_data.get("effect", MoveEffect.HIT)

        if cat == "status":
            # Simple heuristic for status moves
            score = 0
            if effect in (MoveEffect.CHANGE_TARGET_ATK, MoveEffect.CHANGE_TARGET_SPATK):
                param = move_data.get("effect_param", 1)
                stat_key = "atk" if effect == MoveEffect.CHANGE_TARGET_ATK else "spa"
                if pokemon.stat_changes.get(stat_key, 0) < 4:
                    score = 40 * param
            elif effect == MoveEffect.BURN and opponent.can_be_burned():
                score = 50 if move_data["category"] == "status" else 30
            elif effect == MoveEffect.TOXIC and opponent.can_be_poisoned():
                score = 55
            elif effect == MoveEffect.PARALYZE and opponent.can_be_paralyzed():
                score = 45
            elif effect == MoveEffect.STEALTH_ROCK_EFFECT:
                if not (state.team_status[0] & TeamStatus.STEALTH_ROCK):
                    score = 60
            elif effect == MoveEffect.HEAL:
                if pokemon.current_hp < pokemon.max_hp * 0.5:
                    score = 65
            # Small random factor so AI isn't perfectly predictable
            score += random.randint(0, 10)
        else:
            # Damaging move score
            power = move_data["power"]
            if power == 0:
                continue

            power = _calc_base_power(pokemon, opponent, move_name, move_data, state)

            if cat == "physical":
                atk_stat = pokemon.get_effective_stat("atk")
                def_stat = opponent.get_effective_stat("def")
            else:
                atk_stat = pokemon.get_effective_stat("spa")
                def_stat = opponent.get_effective_stat("spd")

            base = ((2 * pokemon.level / 5 + 2) * power * atk_stat / max(1, def_stat)) / 50 + 2
            type_mult = get_type_multiplier(move_data["type"], opponent.types)

            # Levitate immunity
            if move_data["type"] == "Ground" and opponent.ability == "Levitate":
                type_mult = 0

            stab = 1.5 if move_data["type"] in pokemon.types else 1.0
            acc = move_data["accuracy"] if move_data["accuracy"] > 0 else 100

            score = base * type_mult * stab * (acc / 100.0)
            # Penalize recoil
            if effect == MoveEffect.RECOIL:
                score *= 0.85
            score += random.randint(0, 5)

        if score > best_score:
            best_score = score
            best_move = move_name

    return best_move if best_move else pokemon.moves[0]


# =====================================================================
#  Get effective speed (for turn order)
# =====================================================================
def get_effective_speed(pokemon, state):
    """Calculate effective speed including stat stages, paralysis, abilities, items, weather."""
    speed = pokemon.get_effective_stat("spe")

    # Paralysis halves speed
    if pokemon.status1 == Status1.PARALYZED and pokemon.ability != "Quick Feet":
        speed = speed // 2

    # Quick Feet: 1.5x speed when statused
    if pokemon.ability == "Quick Feet" and pokemon.has_status1():
        speed = int(speed * 1.5)

    # Chlorophyll / Swift Swim / Sand Rush
    if pokemon.ability == "Chlorophyll" and state.weather == Weather.HARSH_SUNLIGHT:
        speed *= 2
    if pokemon.ability == "Swift Swim" and state.weather == Weather.RAIN:
        speed *= 2
    if pokemon.ability == "Sand Rush" and state.weather == Weather.SANDSTORM:
        speed *= 2

    # Slow Start
    if pokemon.ability == "Slow Start" and pokemon.slow_start_turns < 5:
        speed = speed // 2

    # Unburden: would need item-loss tracking (simplified: skip)

    # Choice Scarf
    if pokemon.item == "Choice Scarf":
        speed = int(speed * 1.5)

    # Tailwind
    side = 0  # caller should handle this; simplified for 1v1
    # Tailwind is handled in determine_turn_order

    return max(1, speed)


# =====================================================================
#  Determine turn order
# =====================================================================
def determine_turn_order(player_poke, enemy_poke, player_move, enemy_move, state):
    """Returns ('player', 'enemy') or ('enemy', 'player') based on speed/priority."""
    p_data = player_poke.get_move_data(player_move) or {}
    e_data = enemy_poke.get_move_data(enemy_move) or {}

    p_priority = p_data.get("priority", 0)
    e_priority = e_data.get("priority", 0)

    if p_priority != e_priority:
        if p_priority > e_priority:
            return "player", "enemy"
        return "enemy", "player"

    p_speed = get_effective_speed(player_poke, state)
    e_speed = get_effective_speed(enemy_poke, state)

    # Tailwind
    if state.tailwind_turns[0] > 0:
        p_speed *= 2
    if state.tailwind_turns[1] > 0:
        e_speed *= 2

    # Trick Room: slower goes first
    if state.battle_status & BattleStatus.TRICK_ROOM:
        if p_speed != e_speed:
            if p_speed < e_speed:
                return "player", "enemy"
            return "enemy", "player"
    else:
        if p_speed != e_speed:
            if p_speed > e_speed:
                return "player", "enemy"
            return "enemy", "player"

    # Speed tie: random
    if random.randint(0, 1) == 0:
        return "player", "enemy"
    return "enemy", "player"


# =====================================================================
#  Execute a single move  (the main entry point for UI)
# =====================================================================
def execute_move(attacker, defender, move_name, state=None, attacker_side=0):
    """
    Execute a move. Returns list of event dicts for UI.
    state: BattleState (created if None for backward compat).
    attacker_side: 0=player, 1=enemy.
    """
    if state is None:
        state = BattleState()

    events = []
    move_data = attacker.get_move_data(move_name)
    if not move_data:
        events.append({"type": "fail", "user": attacker.species, "move": move_name})
        return events

    events.append({"type": "use_move", "user": attacker.species, "move": move_name,
                    "move_type": move_data["type"]})

    # --- Pre-move status checks ---
    if not _pre_move_status_check(attacker, events):
        attacker.last_move_used = None
        return events

    # --- Defrost on fire moves ---
    flags = move_data.get("flags", MoveFlag.NONE)
    if (flags & MoveFlag.DEFROST_USER) and attacker.status1 == Status1.FROZEN:
        attacker.status1 = Status1.NONE
        events.append({"type": "status_cure", "target": attacker.species, "status": "freeze"})

    # --- Protect check ---
    if defender.has_status2(Status2.PROTECTED):
        events.append({"type": "protected", "target": defender.species})
        return events

    attacker.last_move_used = move_name

    # --- Status moves ---
    cat = move_data["category"]
    if cat == "status":
        # Accuracy check for status moves that have accuracy
        if move_data["accuracy"] > 0:
            if not _accuracy_check(attacker, defender, move_data, state):
                events.append({"type": "miss"})
                return events
        _execute_status_move(attacker, defender, move_name, move_data, events, state, attacker_side)
        # Reset protect counter if move wasn't Protect
        eff = move_data.get("effect", MoveEffect.HIT)
        if eff != MoveEffect.PROTECT:
            attacker.protect_counter = 0
        return events

    # Reset protect counter for damaging moves
    attacker.protect_counter = 0

    # --- Accuracy check ---
    if not _accuracy_check(attacker, defender, move_data, state):
        events.append({"type": "miss"})
        return events

    # --- Damage calculation ---
    crit = _crit_check(attacker, move_data)

    # Ability immunity checks
    mtype = move_data["type"]
    if mtype == "Water" and defender.ability in ("Water Absorb", "Dry Skin"):
        healed = defender.heal(defender.max_hp // 4)
        events.append({"type": "ability_immune", "target": defender.species,
                       "ability": defender.ability, "healed": healed})
        return events
    if mtype == "Electric" and defender.ability in ("Volt Absorb", "Lightning Rod"):
        if defender.ability == "Volt Absorb":
            healed = defender.heal(defender.max_hp // 4)
            events.append({"type": "ability_immune", "target": defender.species,
                           "ability": "Volt Absorb", "healed": healed})
        else:
            actual = defender.change_stat("spa", 1)
            events.append({"type": "ability_immune", "target": defender.species,
                           "ability": "Lightning Rod", "healed": 0})
        return events
    if mtype == "Fire" and defender.ability == "Flash Fire":
        defender.flash_fire_activated = True
        events.append({"type": "ability_immune", "target": defender.species,
                       "ability": "Flash Fire", "healed": 0})
        return events
    if mtype == "Grass" and defender.ability == "Sap Sipper":
        actual = defender.change_stat("atk", 1)
        events.append({"type": "ability_immune", "target": defender.species,
                       "ability": "Sap Sipper", "healed": 0})
        return events
    if mtype == "Ground" and defender.ability == "Levitate":
        events.append({"type": "immune", "target": defender.species})
        return events

    # Screen-side awareness for damage calc
    damage, type_mult, is_crit = calc_damage(attacker, defender, move_name, move_data, state, crit)

    if type_mult == 0:
        events.append({"type": "immune", "target": defender.species})
        return events

    # Report effectiveness
    if type_mult >= 2.0:
        events.append({"type": "effective", "multiplier": type_mult})
    elif 0 < type_mult <= 0.5:
        events.append({"type": "effective", "multiplier": type_mult})

    if is_crit:
        events.append({"type": "critical_hit"})

    # Deal damage
    actual_dmg = defender.deal_damage(damage)
    events.append({
        "type": "damage", "target": defender.species,
        "damage": actual_dmg, "hp": defender.current_hp, "max_hp": defender.max_hp,
    })

    # --- Post-hit effects ---
    effect = move_data.get("effect", MoveEffect.HIT)

    # Recoil
    if effect == MoveEffect.RECOIL and attacker.ability != "Rock Head":
        divisor = move_data.get("recoil_divisor", 3)
        recoil = max(1, actual_dmg // divisor)
        attacker.current_hp = max(0, attacker.current_hp - recoil)
        events.append({"type": "recoil", "target": attacker.species, "damage": recoil,
                       "hp": attacker.current_hp, "max_hp": attacker.max_hp})

    # HP Drain (Giga Drain, Drain Punch)
    if effect == MoveEffect.HP_DRAIN:
        heal_amount = max(1, actual_dmg // 2)
        healed = attacker.heal(heal_amount)
        events.append({"type": "drain", "target": attacker.species, "amount": healed,
                       "hp": attacker.current_hp, "max_hp": attacker.max_hp})

    # Self-Destruct
    if effect == MoveEffect.SELF_DESTRUCT:
        attacker.current_hp = 0
        events.append({"type": "faint", "target": attacker.species})

    # Rapid Spin
    if effect == MoveEffect.RAPID_SPIN:
        _rapid_spin_clear(attacker_side, state, events, attacker)

    # Secondary effects
    if not defender.is_fainted():
        _apply_secondary_effect(attacker, defender, move_data, events, state)

    # Contact abilities (Iron Barbs, Rough Skin, Flame Body, etc.)
    if (flags & MoveFlag.MAKES_CONTACT) and not defender.is_fainted():
        if defender.ability == "Iron Barbs" or defender.ability == "Rough Skin":
            dmg = max(1, attacker.max_hp // 8)
            attacker.current_hp = max(0, attacker.current_hp - dmg)
            events.append({"type": "ability_contact_damage", "target": attacker.species,
                           "ability": defender.ability, "damage": dmg,
                           "hp": attacker.current_hp, "max_hp": attacker.max_hp})
        if defender.ability == "Flame Body" and random.randint(1, 100) <= 30:
            if attacker.can_be_burned():
                attacker.status1 = Status1.BURNED
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Flame Body", "status": "burn"})
        if defender.ability == "Static" and random.randint(1, 100) <= 30:
            if attacker.can_be_paralyzed():
                attacker.status1 = Status1.PARALYZED
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Static", "status": "paralysis"})
        if defender.ability == "Poison Point" and random.randint(1, 100) <= 30:
            if attacker.can_be_poisoned():
                attacker.status1 = Status1.POISONED
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Poison Point", "status": "poison"})
        if defender.ability == "Effect Spore" and random.randint(1, 100) <= 30:
            roll = random.randint(1, 3)
            if roll == 1 and attacker.can_be_poisoned():
                attacker.status1 = Status1.POISONED
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Effect Spore", "status": "poison"})
            elif roll == 2 and attacker.can_be_paralyzed():
                attacker.status1 = Status1.PARALYZED
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Effect Spore", "status": "paralysis"})
            elif roll == 3 and attacker.can_be_put_to_sleep():
                attacker.status1 = Status1.ASLEEP
                attacker.sleep_turns = random.randint(1, 3)
                attacker.sleep_counter = 0
                events.append({"type": "ability_status", "target": attacker.species,
                               "ability": "Effect Spore", "status": "sleep"})

    # Rocky Helmet
    if (flags & MoveFlag.MAKES_CONTACT) and defender.item == "Rocky Helmet" and not defender.is_fainted():
        dmg = max(1, attacker.max_hp // 6)
        attacker.current_hp = max(0, attacker.current_hp - dmg)
        events.append({"type": "item_damage", "target": attacker.species, "item": "Rocky Helmet",
                       "damage": dmg, "hp": attacker.current_hp, "max_hp": attacker.max_hp})

    # Life Orb recoil (if not Sheer Force / Magic Guard)
    if attacker.item == "Life Orb" and attacker.ability not in ("Sheer Force", "Magic Guard"):
        lo_dmg = max(1, attacker.max_hp // 10)
        attacker.current_hp = max(0, attacker.current_hp - lo_dmg)
        events.append({"type": "item_damage", "target": attacker.species, "item": "Life Orb",
                       "damage": lo_dmg, "hp": attacker.current_hp, "max_hp": attacker.max_hp})

    # Moxie: +1 Atk on KO
    if defender.is_fainted() and attacker.ability == "Moxie":
        actual = attacker.change_stat("atk", 1)
        if actual:
            events.append({"type": "ability_stat", "target": attacker.species,
                           "ability": "Moxie", "stat": "Attack", "amount": 1})

    # Faint checks
    if defender.is_fainted():
        events.append({"type": "faint", "target": defender.species})
    if attacker.is_fainted():
        events.append({"type": "faint", "target": attacker.species})

    return events
