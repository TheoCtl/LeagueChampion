"""
Pokemon League Champion - Pokemon & Trainer Models
"""
import math
from data import POKEMON_DB, MOVES_DB


class Pokemon:
    """A single Pokemon instance with stats, level, HP, and moves."""

    def __init__(self, species, level, moves=None):
        if species not in POKEMON_DB:
            raise ValueError(f"Unknown species: {species}")
        self.species = species
        data = POKEMON_DB[species]
        self.types = list(data["types"])
        self.base_stats = dict(data["stats"])
        self.learnable_moves = list(data["learnable_moves"])
        self.level = level
        self.moves = moves if moves else self.learnable_moves[:2]
        # Validate moves exist
        self.moves = [m for m in self.moves if m in MOVES_DB]
        if not self.moves:
            self.moves = ["Tackle"]
        self._calc_stats()
        self.current_hp = self.max_hp

    def _calc_stats(self):
        """Calculate actual stats from base stats and level (simplified formula)."""
        lv = self.level
        base = self.base_stats
        # Simplified stat formula inspired by main games
        self.max_hp = int((2 * base["hp"] * lv / 100) + lv + 10)
        self.atk = int((2 * base["atk"] * lv / 100) + 5)
        self.defense = int((2 * base["def"] * lv / 100) + 5)
        self.spa = int((2 * base["spa"] * lv / 100) + 5)
        self.spd = int((2 * base["spd"] * lv / 100) + 5)
        self.spe = int((2 * base["spe"] * lv / 100) + 5)

    def is_fainted(self):
        return self.current_hp <= 0

    def heal_full(self):
        self.current_hp = self.max_hp

    def level_up(self, levels=1):
        self.level += levels
        self._calc_stats()
        self.current_hp = self.max_hp

    def get_move_data(self, move_name):
        if move_name in MOVES_DB:
            return MOVES_DB[move_name]
        return None

    def __str__(self):
        return f"{self.species} Lv.{self.level} ({self.current_hp}/{self.max_hp} HP)"

    def status_bar(self):
        """Return a visual HP bar."""
        bar_len = 20
        ratio = max(0, self.current_hp / self.max_hp)
        filled = int(bar_len * ratio)
        bar = "█" * filled + "░" * (bar_len - filled)
        types_str = "/".join(self.types)
        return f"{self.species} Lv.{self.level} [{types_str}]  HP: {self.current_hp}/{self.max_hp} |{bar}|"


class Trainer:
    """A trainer with a name, title, and team of Pokemon."""

    def __init__(self, name, title, team_data, specialty=None):
        self.name = name
        self.title = title
        self.specialty = specialty
        self.team = []
        for pdata in team_data:
            poke = Pokemon(pdata["species"], pdata["level"], pdata.get("moves"))
            self.team.append(poke)

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
        return [
            {"species": p.species, "level": p.level, "moves": list(p.moves)}
            for p in self.team
        ]
