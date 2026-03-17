"""
Pokemon League Champion - Pokemon & Trainer Models
Full battle-state support: abilities, items, natures, status, stat stages.
"""
import math, random
from data import POKEMON_DB, MOVES_DB, NATURES, TYPE_TIERS, EVOLVES_FROM
from enums import Status1, Status2, MoveFlag


class Pokemon:
    """A single Pokemon instance with full competitive battle state."""

    def __init__(self, species, level, moves=None, ability=None, item=None, nature=None, move_tier_levels=None):
        if species not in POKEMON_DB:
            raise ValueError(f"Unknown species: {species}")
        self.species = species
        data = POKEMON_DB[species]
        self.types = list(data["types"])
        self.base_stats = dict(data["stats"])
        self.move_tiers = dict(data.get("move_tiers", {}))
        self.level = level

        # --- Determine moves from tier system or direct assignment ---
        if move_tier_levels is not None:
            self.move_tier_levels = dict(move_tier_levels)
            self._update_moves_from_tiers()
        elif moves is not None:
            self.moves = [m for m in moves if m in MOVES_DB]
            if not self.moves:
                self.moves = ["Tackle"]
            # Derive tier levels from assigned moves
            self.move_tier_levels = {}
            for mtype, tier_list in self.move_tiers.items():
                for i, mv in enumerate(tier_list):
                    if mv in self.moves:
                        self.move_tier_levels[mtype] = i + 1
        else:
            # Default: tier 1 of first move type only
            self.move_tier_levels = {}
            for mtype, tier_list in self.move_tiers.items():
                if tier_list:
                    self.move_tier_levels[mtype] = 1
                    break
            self._update_moves_from_tiers()

        # ----- Ability / Item / Nature -----
        available_abilities = data.get("abilities", ["Pressure"])
        if ability and ability in available_abilities:
            self.ability = ability
        else:
            self.ability = available_abilities[0]
        self.item = item  # string name or None
        self.nature = nature or "Hardy"  # neutral by default

        # ----- Computed stats -----
        self._calc_stats()
        self.current_hp = self.max_hp

        # ----- Battle-only state (reset on switch-in / battle start) -----
        self.reset_battle_state()

    # ── Stat calculation ────────────────────────────────────────────
    def _calc_stats(self):
        lv = self.level
        base = self.base_stats
        nat = NATURES.get(self.nature)

        self.max_hp = int((2 * base["hp"] * lv / 100) + lv + 10)

        for stat_key, attr in [("atk", "atk"), ("def", "defense"),
                                ("spa", "spa"), ("spd", "spd"), ("spe", "spe")]:
            value = int((2 * base[stat_key] * lv / 100) + 5)
            # Nature modifier
            if nat:
                boosted, lowered = nat
                if boosted == stat_key:
                    value = int(value * 1.1)
                elif lowered == stat_key:
                    value = int(value * 0.9)
            setattr(self, attr, value)

    # ── Moves from tier system ────────────────────────────────────────
    def _update_moves_from_tiers(self):
        """Rebuild self.moves from move_tier_levels."""
        self.moves = []
        for mtype, tier_level in self.move_tier_levels.items():
            tier_list = self.move_tiers.get(mtype, [])
            if 0 < tier_level <= len(tier_list):
                self.moves.append(tier_list[tier_level - 1])

    def get_available_move_upgrades(self):
        """Return list of (move_type, current_tier, max_tier) for upgradeable types."""
        upgrades = []
        for mtype, tier_list in self.move_tiers.items():
            cur = self.move_tier_levels.get(mtype, 0)
            max_t = len(tier_list)
            if cur > 0 and cur < max_t:
                upgrades.append((mtype, cur, max_t))
        return upgrades

    def get_learnable_new_types(self):
        """Return move types this Pokemon can learn but hasn't yet (max 4 types)."""
        if len(self.move_tier_levels) >= 4:
            return []
        new_types = []
        for mtype in self.move_tiers:
            if mtype not in self.move_tier_levels:
                new_types.append(mtype)
        return new_types

    def upgrade_move_type(self, move_type):
        """Upgrade a move type by one tier, or learn a new type at tier 1. Returns new move name."""
        tier_list = self.move_tiers.get(move_type, [])
        if not tier_list:
            return None
        cur = self.move_tier_levels.get(move_type, 0)
        if cur >= len(tier_list):
            return None
        self.move_tier_levels[move_type] = cur + 1
        self._update_moves_from_tiers()
        return tier_list[cur]

    # ── Battle state ────────────────────────────────────────────────
    def reset_battle_state(self):
        """Reset volatile battle state (called on switch-in or battle start)."""
        self.stat_changes = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "acc": 0, "eva": 0}
        self.status1 = Status1.NONE
        self.status2 = Status2(0)
        self.substitute_hp = 0
        self.sleep_turns = 0
        self.sleep_counter = 0
        self.confusion_turns = 0
        self.confusion_counter = 0
        self.badly_poisoned_counter = 0
        self.protect_counter = 0
        self.last_move_used = None
        # Ability-specific trackers
        self.flash_fire_activated = False
        self.slow_start_turns = 0
        self.speed_boost_count = 0

    def get_stat_stage_multiplier(self, stat_key):
        """Return the multiplier for a stat stage change (±6 range).
        For acc/eva the base numerator/denominator is 3; for others it's 2."""
        stage = self.stat_changes.get(stat_key, 0)
        if stat_key in ("acc", "eva"):
            base = 3
        else:
            base = 2
        if stage >= 0:
            return (base + stage) / base
        else:
            return base / (base - stage)

    def get_effective_stat(self, stat_key):
        """Return the stat value modified by stage changes (before ability/item)."""
        raw_map = {"atk": self.atk, "def": self.defense, "spa": self.spa,
                   "spd": self.spd, "spe": self.spe}
        if stat_key not in raw_map:
            return 1
        return max(1, int(raw_map[stat_key] * self.get_stat_stage_multiplier(stat_key)))

    def change_stat(self, stat_key, amount):
        """Apply a stat stage change. Returns the actual change applied."""
        old = self.stat_changes.get(stat_key, 0)
        new = max(-6, min(6, old + amount))
        self.stat_changes[stat_key] = new
        return new - old

    def clear_stat_changes(self):
        for k in self.stat_changes:
            self.stat_changes[k] = 0

    def has_type(self, type_name):
        return type_name in self.types

    def is_grounded(self):
        """Check if the Pokemon is grounded (affected by ground moves / spikes)."""
        if "Flying" in self.types:
            return False
        if self.ability == "Levitate":
            return False
        return True

    # ── Status helpers ──────────────────────────────────────────────
    def has_status1(self):
        return self.status1 != Status1.NONE

    def has_status2(self, flag):
        return bool(self.status2 & flag)

    def set_status2(self, flag):
        self.status2 = Status2(self.status2 | flag)

    def clear_status2(self, flag):
        self.status2 = Status2(self.status2 & ~flag)

    def can_be_poisoned(self):
        if self.has_status1():
            return False
        if "Poison" in self.types or "Steel" in self.types:
            return False
        if self.ability == "Immunity":
            return False
        return True

    def can_be_burned(self):
        if self.has_status1():
            return False
        if "Fire" in self.types:
            return False
        if self.ability == "Water Veil":
            return False
        return True

    def can_be_paralyzed(self):
        if self.has_status1():
            return False
        if "Electric" in self.types:
            return False
        if self.ability == "Limber":
            return False
        return True

    def can_be_frozen(self):
        if self.has_status1():
            return False
        if "Ice" in self.types:
            return False
        if self.ability == "Magma Armor":
            return False
        return True

    def can_be_put_to_sleep(self):
        if self.has_status1():
            return False
        if self.ability in ("Insomnia", "Vital Spirit"):
            return False
        return True

    # ── HP / Faint ──────────────────────────────────────────────────
    def is_fainted(self):
        return self.current_hp <= 0

    def deal_damage(self, amount):
        """Deal damage, respecting substitute. Returns actual damage dealt."""
        amount = max(0, int(amount))
        if self.substitute_hp > 0:
            sub_dmg = min(self.substitute_hp, amount)
            self.substitute_hp -= sub_dmg
            return sub_dmg
        dmg = min(self.current_hp, amount)
        self.current_hp = max(0, self.current_hp - dmg)
        return dmg

    def heal(self, amount):
        """Heal HP. Returns actual amount healed."""
        amount = max(0, int(amount))
        before = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - before

    def heal_full(self):
        self.current_hp = self.max_hp
        self.status1 = Status1.NONE
        self.status2 = Status2(0)
        self.badly_poisoned_counter = 0

    def level_up(self, levels=1):
        self.level += levels
        self._calc_stats()
        self.current_hp = self.max_hp

    def get_move_data(self, move_name):
        if move_name in MOVES_DB:
            return MOVES_DB[move_name]
        return None

    def __str__(self):
        status = ""
        if self.status1 != Status1.NONE:
            status = f" [{self.status1.name[:3]}]"
        return f"{self.species} Lv.{self.level} ({self.current_hp}/{self.max_hp} HP){status}"

    def status_bar(self):
        bar_len = 20
        ratio = max(0, self.current_hp / self.max_hp)
        filled = int(bar_len * ratio)
        bar = "█" * filled + "░" * (bar_len - filled)
        types_str = "/".join(self.types)
        status = ""
        if self.status1 != Status1.NONE:
            status = f" [{self.status1.name[:3]}]"
        return f"{self.species} Lv.{self.level} [{types_str}]  HP: {self.current_hp}/{self.max_hp} |{bar}|{status}"


class Trainer:
    """A trainer with a name, title, and team of Pokemon."""

    def __init__(self, name, title, team_data, specialty=None):
        self.name = name
        self.title = title
        self.specialty = specialty
        self.team = []
        self.ever_had = set()
        for pdata in team_data:
            poke = Pokemon(pdata["species"], pdata["level"], pdata.get("moves"),
                          ability=pdata.get("ability"), item=pdata.get("item"),
                          nature=pdata.get("nature"),
                          move_tier_levels=pdata.get("move_tier_levels"))
            self.team.append(poke)
            self.ever_had.add(pdata["species"])

        # Mark all lower-tier Pokemon as "ever had" for the specialty
        if self.specialty and self.specialty in TYPE_TIERS:
            tiers = TYPE_TIERS[self.specialty]
            max_idx = -1
            for p in self.team:
                if p.species in tiers:
                    idx = tiers.index(p.species)
                    max_idx = max(max_idx, idx)
            for i in range(max_idx + 1):
                self.ever_had.add(tiers[i])

    def has_pokemon_left(self):
        return any(not p.is_fainted() for p in self.team)

    def first_available(self):
        for p in self.team:
            if not p.is_fainted():
                return p
        return None

    def heal_all(self):
        for p in self.team:
            p.heal_full()

    def get_next_tier_pokemon(self):
        """Return the next species in this trainer's type tier, or None."""
        if not self.specialty or self.specialty not in TYPE_TIERS:
            return None
        for species in TYPE_TIERS[self.specialty]:
            if species not in self.ever_had:
                return species
        return None

    def add_tier_pokemon(self, species, level):
        """Add a tier Pokemon. If it evolves from someone on the team, replace them."""
        pre_evo = EVOLVES_FROM.get(species)
        replaced = False
        if pre_evo:
            for i, p in enumerate(self.team):
                if p.species == pre_evo:
                    self.team[i] = Pokemon(species, level)
                    replaced = True
                    break
        if not replaced:
            self.team.append(Pokemon(species, level))
        self.ever_had.add(species)

    def display_name(self):
        return f"{self.title} {self.name}"

    def team_summary(self):
        lines = [f"  {self.display_name()}'s team:"]
        for i, p in enumerate(self.team):
            status = "FAINTED" if p.is_fainted() else f"{p.current_hp}/{p.max_hp} HP"
            lines.append(f"    {i+1}. {p.species} Lv.{p.level} - {status}")
        return "\n".join(lines)

    def get_team_data(self):
        """Serialize team back to data format (for saving/upgrades)."""
        result = []
        for p in self.team:
            entry = {"species": p.species, "level": p.level, "moves": list(p.moves)}
            if p.move_tier_levels:
                entry["move_tier_levels"] = dict(p.move_tier_levels)
            result.append(entry)
        return result
