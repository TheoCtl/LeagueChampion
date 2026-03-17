"""
Pokemon League Champion - Battle Enums & Constants
Ported from PokemonBattleEngine (Kermalis) C# source.
"""
from enum import Enum, Flag, auto


# ─── Status Conditions (non-volatile, only one at a time) ───────────
class Status1(Enum):
    NONE = 0
    ASLEEP = auto()
    BURNED = auto()
    FROZEN = auto()
    PARALYZED = auto()
    POISONED = auto()
    BADLY_POISONED = auto()


# ─── Volatile Status (bit flags, multiple can coexist) ──────────────
class Status2(Flag):
    NONE = 0
    CONFUSED = auto()
    FLINCHING = auto()
    INFATUATED = auto()
    LEECH_SEED = auto()
    PROTECTED = auto()
    SUBSTITUTE = auto()
    CURSED = auto()
    IDENTIFIED = auto()     # Foresight / Odor Sleuth
    PUMPED = auto()         # Focus Energy
    NIGHTMARE = auto()


# ─── Weather ────────────────────────────────────────────────────────
class Weather(Enum):
    NONE = 0
    HARSH_SUNLIGHT = auto()
    RAIN = auto()
    SANDSTORM = auto()
    HAILSTORM = auto()


# ─── Team-side Status (entry hazards, screens) ──────────────────────
class TeamStatus(Flag):
    NONE = 0
    REFLECT = auto()
    LIGHT_SCREEN = auto()
    SPIKES = auto()
    STEALTH_ROCK = auto()
    TOXIC_SPIKES = auto()
    TAILWIND = auto()
    LUCKY_CHANT = auto()
    SAFEGUARD = auto()


# ─── Battle-wide Status ────────────────────────────────────────────
class BattleStatus(Flag):
    NONE = 0
    TRICK_ROOM = auto()


# ─── Move Category ─────────────────────────────────────────────────
class MoveCategory(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


# ─── Move Effect (for moves with special behavior) ─────────────────
class MoveEffect(Enum):
    HIT = "hit"
    # Status inflicting
    BURN = "burn"
    PARALYZE = "paralyze"
    POISON = "poison"
    TOXIC = "toxic"
    SLEEP = "sleep"
    CONFUSE = "confuse"
    # Stat changing (target)
    CHANGE_TARGET_ATK = "change_target_atk"
    CHANGE_TARGET_DEF = "change_target_def"
    CHANGE_TARGET_SPATK = "change_target_spatk"
    CHANGE_TARGET_SPDEF = "change_target_spdef"
    CHANGE_TARGET_SPE = "change_target_spe"
    CHANGE_TARGET_ACC = "change_target_acc"
    CHANGE_TARGET_EVA = "change_target_eva"
    # Hit + maybe inflict
    HIT_MAYBE_BURN = "hit_maybe_burn"
    HIT_MAYBE_FREEZE = "hit_maybe_freeze"
    HIT_MAYBE_PARALYZE = "hit_maybe_paralyze"
    HIT_MAYBE_POISON = "hit_maybe_poison"
    HIT_MAYBE_CONFUSE = "hit_maybe_confuse"
    HIT_MAYBE_FLINCH = "hit_maybe_flinch"
    HIT_MAYBE_LOWER_TARGET_DEF = "hit_maybe_lower_target_def"
    HIT_MAYBE_LOWER_TARGET_SPDEF = "hit_maybe_lower_target_spdef"
    HIT_MAYBE_LOWER_TARGET_SPATK = "hit_maybe_lower_target_spatk"
    HIT_MAYBE_LOWER_TARGET_SPE = "hit_maybe_lower_target_spe"
    HIT_MAYBE_LOWER_TARGET_ACC = "hit_maybe_lower_target_acc"
    HIT_MAYBE_RAISE_USER_ATK = "hit_maybe_raise_user_atk"
    HIT_MAYBE_RAISE_USER_SPATK = "hit_maybe_raise_user_spatk"
    HIT_MAYBE_RAISE_USER_SPE = "hit_maybe_raise_user_spe"
    HIT_MAYBE_RAISE_USER_DEF = "hit_maybe_raise_user_def"
    HIT_BURN_FREEZE_PARA = "hit_burn_freeze_para"  # Tri Attack
    # Special damage
    RECOIL = "recoil"
    HP_DRAIN = "hp_drain"
    FIXED_DAMAGE = "fixed_damage"      # Seismic Toss / Dragon Rage
    SUPER_FANG = "super_fang"
    ERUPTION = "eruption"
    FLAIL = "flail"
    BRINE = "brine"
    HEX_EFFECT = "hex_effect"
    FACADE = "facade"
    VENOSHOCK = "venoshock"
    ACROBATICS = "acrobatics"
    PSYSHOCK_EFFECT = "psyshock_effect"  # Special move that targets Defense
    # Multi-hit
    HIT_2_TIMES = "hit_2_times"
    HIT_2_TO_5 = "hit_2_to_5"
    # Weather
    SUNNY_DAY = "sunny_day"
    RAIN_DANCE = "rain_dance"
    SANDSTORM_WEATHER = "sandstorm_weather"
    HAIL = "hail"
    # Team status
    REFLECT_EFFECT = "reflect_effect"
    LIGHT_SCREEN_EFFECT = "light_screen_effect"
    STEALTH_ROCK_EFFECT = "stealth_rock_effect"
    SPIKES_EFFECT = "spikes_effect"
    TOXIC_SPIKES_EFFECT = "toxic_spikes_effect"
    # Other
    PROTECT = "protect"
    SUBSTITUTE_EFFECT = "substitute_effect"
    LEECH_SEED_EFFECT = "leech_seed_effect"
    FOCUS_ENERGY = "focus_energy"
    HEAL = "heal"           # Recover, Roost, etc.
    BELLY_DRUM = "belly_drum"
    RAPID_SPIN = "rapid_spin"
    TRICK_ROOM_EFFECT = "trick_room_effect"
    TAILWIND_EFFECT = "tailwind_effect"
    HAZE = "haze"
    WHIRLWIND = "whirlwind"
    REST = "rest"
    SELF_DESTRUCT = "self_destruct"
    CURSE = "curse_effect"


# ─── Move Flags ─────────────────────────────────────────────────────
class MoveFlag(Flag):
    NONE = 0
    MAKES_CONTACT = auto()
    HIGH_CRIT = auto()
    DEFROST_USER = auto()
    SOUND_BASED = auto()
    PUNCHING = auto()
    BITING = auto()


# ─── Stat Keys ──────────────────────────────────────────────────────
STAT_ATK = "atk"
STAT_DEF = "def"
STAT_SPATK = "spa"
STAT_SPDEF = "spd"
STAT_SPE = "spe"
STAT_ACC = "acc"
STAT_EVA = "eva"

ALL_BATTLE_STATS = [STAT_ATK, STAT_DEF, STAT_SPATK, STAT_SPDEF, STAT_SPE]

# ─── Settings / Constants ──────────────────────────────────────────
MAX_STAT_CHANGE = 6
SLEEP_MIN_TURNS = 1
SLEEP_MAX_TURNS = 3
CONFUSION_MIN_TURNS = 1
CONFUSION_MAX_TURNS = 4
BURN_DAMAGE_DIVISOR = 8
POISON_DAMAGE_DIVISOR = 8
TOXIC_DAMAGE_DIVISOR = 16   # maxHP * counter / 16
HAIL_DAMAGE_DIVISOR = 16
SANDSTORM_DAMAGE_DIVISOR = 16
LEECH_SEED_DIVISOR = 8
WEATHER_DURATION = 5
REFLECT_TURNS = 5
LIGHT_SCREEN_TURNS = 5
TAILWIND_TURNS = 4
TRICK_ROOM_TURNS = 5
SPIKES_MAX = 3
TOXIC_SPIKES_MAX = 2
CRIT_MULTIPLIER = 1.5
