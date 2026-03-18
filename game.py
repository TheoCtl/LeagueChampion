"""
Pokemon League Champion - Game Scenes
All Pygame scenes: Title, Day, Battle, Shop, League Overview, GameOver.
"""
import pygame
import sys
import random
from engine import (
    Scene, Panel, Button, Label, TextInput, HPBar, MessageLog,
    SCREEN_W, SCREEN_H, C_BG, C_BG_LIGHT, C_PANEL, C_PANEL_BORDER,
    C_TEXT, C_TEXT_DIM, C_TEXT_BRIGHT, C_ACCENT, C_GOLD, C_GREEN, C_RED,
    C_YELLOW, C_BTN, C_BTN_HOVER, C_BTN_BORDER,
    draw_text, draw_type_badges, draw_pokemon_card, type_color,
)
from pokemon import Trainer, Pokemon
from battle_logic import (
    ai_choose_move, execute_move, BattleState,
    determine_turn_order, do_turn_end_effects, do_switch_in_effects,
    get_effective_speed,
)
from enums import Status1, Weather
from generator import generate_challenger
from data import (
    DEFAULT_GYM_LEADERS, DEFAULT_ELITE_FOUR,
    POKEMON_DB, MOVES_DB, TYPE_TIERS, EVOLVES_FROM,
)


# ─── Game State (shared across scenes) ─────────────────────────────

class GameState:
    def __init__(self):
        self.league = []
        self.champion = None
        self.player_name = ""
        self.money = 200
        self.day = 1
        self.challengers_beaten = 0
        self.current_challenger = None
        self.challenger_position = 0


# ─── Title Scene ────────────────────────────────────────────────────

class TitleScene(Scene):
    """Name entry + champion draft."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.phase = "name"  # "name" -> "draft"
        self.name_input = TextInput(SCREEN_W // 2 - 150, 380, 300, 44,
                                    placeholder="Enter your name...", font_size=22)
        self.confirm_btn = Button("Confirm", SCREEN_W // 2 - 60, 440, 120, 40,
                                  callback=self._confirm_name, font_size=18)
        self.draft_pairs = []
        self.draft_round = 0
        self.draft_picks = []
        self.draft_buttons = []

    def _confirm_name(self):
        name = self.name_input.text.strip()
        if name:
            self.state.player_name = name
        else:
            self.state.player_name = "Champion"
        self.phase = "draft"
        self._build_draft()

    def _build_draft(self):
        all_species = list(POKEMON_DB.keys())
        chosen = random.sample(all_species, min(12, len(all_species)))
        random.shuffle(chosen)
        self.draft_pairs = [(chosen[i], chosen[i + 1]) for i in range(0, 12, 2)]
        self.draft_round = 0
        self.draft_picks = []
        self._build_draft_buttons()

    def _build_draft_buttons(self):
        if self.draft_round >= len(self.draft_pairs):
            self._finish_draft()
            return
        a, b = self.draft_pairs[self.draft_round]
        self.draft_buttons = [
            Button(f"Pick {a}", 80, 640, 200, 44,
                   callback=lambda: self._draft_pick(a),
                   font_size=18, color=(40, 60, 40), hover_color=(50, 80, 50),
                   border_color=C_GREEN),
            Button(f"Pick {b}", SCREEN_W - 280, 640, 200, 44,
                   callback=lambda: self._draft_pick(b),
                   font_size=18, color=(40, 60, 40), hover_color=(50, 80, 50),
                   border_color=C_GREEN),
        ]

    def _draft_pick(self, species):
        self.draft_picks.append(species)
        self.draft_round += 1
        self._build_draft_buttons()

    def _finish_draft(self):
        team_data = []
        for species in self.draft_picks:
            pdata = POKEMON_DB[species]
            mt = pdata.get("move_tiers", {})
            max_tiers = {mtype: len(tlist) for mtype, tlist in mt.items()}
            team_data.append({"species": species, "level": 50, "move_tier_levels": max_tiers})
        gym_leaders = []
        for gl_data in DEFAULT_GYM_LEADERS:
            gym_leaders.append(Trainer(gl_data["name"], gl_data["title"],
                                       gl_data["team"], gl_data.get("specialty")))
        elite_four = []
        for e4_data in DEFAULT_ELITE_FOUR:
            elite_four.append(Trainer(e4_data["name"], e4_data["title"],
                                      e4_data["team"], e4_data.get("specialty")))
        champion = Trainer(self.state.player_name, "Champion", team_data)
        self.state.league = gym_leaders + elite_four + [champion]
        self.state.champion = champion
        self.engine.set_scene(DayScene(self.state))

    def handle_events(self, events):
        for e in events:
            if self.phase == "name":
                result = self.name_input.handle_event(e)
                if result == "submit":
                    self._confirm_name()
                self.confirm_btn.handle_event(e)
            elif self.phase == "draft":
                for btn in self.draft_buttons:
                    btn.handle_event(e)

    def update(self, dt):
        if self.phase == "name":
            self.name_input.update(dt)

    def draw(self, screen):
        screen.fill(C_BG)

        draw_text(screen, self.engine, "POKEMON LEAGUE CHAMPION",
                  SCREEN_W // 2, 30, 42, C_GOLD, anchor="midtop")
        draw_text(screen, self.engine, "Defend your title. Manage your League.",
                  SCREEN_W // 2, 80, 18, C_TEXT_DIM, anchor="midtop")

        if self.phase == "name":
            draw_text(screen, self.engine, "What is your name, Champion?",
                      SCREEN_W // 2, 320, 24, C_ACCENT, anchor="midtop")
            self.name_input.draw(screen, self.engine)
            self.confirm_btn.draw(screen, self.engine)

        elif self.phase == "draft":
            if self.draft_round < len(self.draft_pairs):
                draw_text(screen, self.engine,
                          f"CHAMPION DRAFT — Round {self.draft_round + 1}/6",
                          SCREEN_W // 2, 110, 26, C_ACCENT, anchor="midtop")
                draw_text(screen, self.engine, "Choose one Pokemon from each pair:",
                          SCREEN_W // 2, 142, 16, C_TEXT_DIM, anchor="midtop")

                a, b = self.draft_pairs[self.draft_round]
                self._draw_draft_card(screen, a, 40, 170, SCREEN_W // 2 - 60)
                self._draw_draft_card(screen, b, SCREEN_W // 2 + 20, 170, SCREEN_W // 2 - 60)

                draw_text(screen, self.engine, "OR",
                          SCREEN_W // 2, 400, 28, C_GOLD, anchor="center")

                for btn in self.draft_buttons:
                    btn.draw(screen, self.engine)

            if self.draft_picks:
                draw_text(screen, self.engine, "Your picks:",
                          SCREEN_W // 2, 700, 14, C_TEXT_DIM, anchor="midtop")
                picks_str = ", ".join(self.draft_picks)
                draw_text(screen, self.engine, picks_str,
                          SCREEN_W // 2, 718, 14, C_GREEN, anchor="midtop")

    def _draw_draft_card(self, screen, species, x, y, w):
        pdata = POKEMON_DB[species]
        panel = Panel(x, y, w, 440)
        panel.draw(screen, self.engine)

        draw_text(screen, self.engine, species, x + 20, y + 10, 24, C_TEXT_BRIGHT)
        draw_type_badges(screen, self.engine, pdata["types"], x + 20, y + 40)

        stats = pdata["stats"]
        sy = y + 70
        for stat_name in ["hp", "atk", "def", "spa", "spd", "spe"]:
            draw_text(screen, self.engine,
                      f"{stat_name.upper()}: {stats[stat_name]}",
                      x + 20, sy, 14, C_TEXT)
            sy += 18

        sy += 8
        draw_text(screen, self.engine, "Move Types:", x + 20, sy, 14, C_ACCENT)
        sy += 20
        for mtype, tlist in pdata.get("move_tiers", {}).items():
            moves_str = " > ".join(tlist)
            draw_text(screen, self.engine,
                      f"  {mtype}: {moves_str}",
                      x + 20, sy, 12, C_TEXT_DIM)
            sy += 16


# ─── Day Scene ──────────────────────────────────────────────────────

class DayScene(Scene):
    """Daily overview: show matchup, let player fight/shop/view."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self._ensure_challenger()
        self.buttons = []
        self._build_buttons()

    def _ensure_challenger(self):
        if self.state.current_challenger is None:
            data = generate_challenger(self.state.challengers_beaten)
            self.state.current_challenger = Trainer(data["name"], data["title"], data["team"])
            self.state.challenger_position = 0

    def _build_buttons(self):
        bx = SCREEN_W // 2 - 120
        self.buttons = [
            Button("Fight!", bx, 580, 240, 42,
                   callback=self._fight, font_size=20,
                   color=(80, 40, 40), hover_color=(120, 50, 50),
                   border_color=C_RED, text_color=C_TEXT_BRIGHT),
            Button("Shop", bx, 630, 240, 42,
                   callback=self._shop, font_size=20,
                   color=(40, 60, 80), hover_color=(50, 80, 120),
                   border_color=C_ACCENT),
            Button("League Overview", bx, 680, 240, 42,
                   callback=self._overview, font_size=20),
            Button("Quit", bx, 730, 240, 36,
                   callback=self._quit, font_size=16,
                   color=(50, 50, 50), hover_color=(70, 50, 50),
                   border_color=C_TEXT_DIM),
        ]

    def _fight(self):
        league_member = self.state.league[self.state.challenger_position]
        league_member.heal_all()
        self.state.current_challenger.heal_all()
        self.engine.set_scene(BattleScene(self.state, league_member, self.state.current_challenger))

    def _shop(self):
        self.engine.set_scene(ShopScene(self.state))

    def _overview(self):
        self.engine.set_scene(LeagueScene(self.state))

    def _quit(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, events):
        for e in events:
            for btn in self.buttons:
                btn.handle_event(e)

    def draw(self, screen):
        screen.fill(C_BG)
        s = self.state

        # Header bar
        header_panel = Panel(20, 15, SCREEN_W - 40, 50, bg=(30, 35, 50))
        header_panel.draw(screen, self.engine)
        draw_text(screen, self.engine, f"DAY {s.day}", 40, 28, 26, C_GOLD)
        draw_text(screen, self.engine, f"${s.money}", 220, 32, 20, C_YELLOW)
        draw_text(screen, self.engine, f"Challengers Defeated: {s.challengers_beaten}",
                  SCREEN_W - 40, 32, 18, C_GREEN, anchor="topright")

        # Matchup panel
        member = s.league[s.challenger_position]
        challenger = s.current_challenger

        draw_text(screen, self.engine, "TODAY'S MATCHUP",
                  SCREEN_W // 2, 85, 22, C_ACCENT, anchor="midtop")

        # Defender side (left)
        panel_w = (SCREEN_W - 80) // 2 - 10
        def_panel = Panel(30, 120, panel_w, 420, title="DEFENDER",
                          border=(60, 140, 80), title_color=C_GREEN)
        def_panel.draw(screen, self.engine)

        draw_text(screen, self.engine, member.display_name(),
                  50, 148, 20, C_TEXT_BRIGHT)
        draw_text(screen, self.engine,
                  f"Stage {s.challenger_position + 1}/{len(s.league)}",
                  50, 172, 14, C_TEXT_DIM)

        dy = 200
        for p in member.team:
            h = draw_pokemon_card(screen, self.engine, p, 45, dy, panel_w - 40, show_moves=True)
            dy += h + 6

        # Challenger side (right)
        chall_x = SCREEN_W // 2 + 10
        chall_panel = Panel(chall_x, 120, panel_w, 420, title="CHALLENGER",
                            border=(180, 60, 60), title_color=C_RED)
        chall_panel.draw(screen, self.engine)

        draw_text(screen, self.engine, challenger.display_name(),
                  chall_x + 20, 148, 20, C_TEXT_BRIGHT)

        cy = 200
        for p in challenger.team:
            h = draw_pokemon_card(screen, self.engine, p, chall_x + 15, cy, panel_w - 40, show_moves=True)
            cy += h + 6

        # VS divider
        draw_text(screen, self.engine, "VS",
                  SCREEN_W // 2, 300, 36, C_GOLD, anchor="center")

        # Buttons
        for btn in self.buttons:
            btn.draw(screen, self.engine)


# ─── Battle Scene ───────────────────────────────────────────────────

class BattleScene(Scene):
    """Interactive battle with graphical UI."""

    def __init__(self, state, player_trainer, enemy_trainer):
        super().__init__()
        self.state = state
        self.player_trainer = player_trainer
        self.enemy_trainer = enemy_trainer
        self.player_poke = player_trainer.first_available()
        self.enemy_poke = enemy_trainer.first_available()
        self.phase = "choose_move"  # "choose_move", "animating", "switch", "done"
        self.log = MessageLog(20, 460, SCREEN_W - 40, 150, font_size=16)
        self.move_buttons = []
        self.switch_buttons = []
        self.done_button = None
        self.anim_events = []
        self.anim_timer = 0
        self.anim_delay = 0.6
        self.result = None  # True = player won, False = lost
        self.battle_state = BattleState()
        # Reset battle state for starting Pokemon
        self.player_poke.reset_battle_state()
        self.enemy_poke.reset_battle_state()
        self._build_move_buttons()
        self.log.add(f"{player_trainer.name} sends out {self.player_poke.species}!", C_GREEN)
        self.log.add(f"{enemy_trainer.name} sends out {self.enemy_poke.species}!", C_RED)
        # Switch-in effects for initial Pokemon
        for ev in do_switch_in_effects(self.player_poke, 0, self.battle_state):
            self._log_event(ev)
        for ev in do_switch_in_effects(self.enemy_poke, 1, self.battle_state):
            self._log_event(ev)
        # Apply Intimidate cross-side
        if self.player_poke.ability == "Intimidate":
            actual = self.enemy_poke.change_stat("atk", -1)
            if actual:
                self.log.add(f"{self.enemy_poke.species}'s Attack fell! (Intimidate)", C_YELLOW)
        if self.enemy_poke.ability == "Intimidate":
            actual = self.player_poke.change_stat("atk", -1)
            if actual:
                self.log.add(f"{self.player_poke.species}'s Attack fell! (Intimidate)", C_YELLOW)

    def _build_move_buttons(self):
        self.move_buttons = []
        if not self.player_poke or self.player_poke.is_fainted():
            return
        for i, move_name in enumerate(self.player_poke.moves):
            md = MOVES_DB.get(move_name, {})
            mtype = md.get("type", "Normal")
            mcolor = type_color(mtype)
            raw_cat = md.get("category", "physical")
            cat = "PHY" if raw_cat == "physical" else ("STA" if raw_cat == "status" else "SPE")
            pw = md.get("power", 0)
            pw_str = str(pw) if pw else "-"
            label = f"{move_name}  ({mtype} {cat} P:{pw_str})"

            col = i % 2
            row = i // 2
            bx = 20 + col * (SCREEN_W // 2 - 20)
            by = 625 + row * 50
            bw = SCREEN_W // 2 - 30

            # Tinted button color based on type
            r, g, b = mcolor
            btn_color = (r // 4 + 20, g // 4 + 20, b // 4 + 20)
            btn_hover = (r // 3 + 30, g // 3 + 30, b // 3 + 30)

            btn = Button(label, bx, by, bw, 42,
                         callback=lambda m=move_name: self._select_move(m),
                         font_size=16, color=btn_color, hover_color=btn_hover,
                         border_color=mcolor, tag=move_name)
            self.move_buttons.append(btn)

    def _build_switch_buttons(self):
        self.switch_buttons = []
        available = [(i, p) for i, p in enumerate(self.player_trainer.team) if not p.is_fainted()]
        for j, (idx, p) in enumerate(available):
            bx = SCREEN_W // 2 - 200
            by = 625 + j * 46
            label = f"{p.species} Lv.{p.level}  HP: {p.current_hp}/{p.max_hp}"
            btn = Button(label, bx, by, 400, 40,
                         callback=lambda poke=p: self._switch_to(poke),
                         font_size=16, color=(40, 60, 50), hover_color=(50, 80, 60),
                         border_color=C_GREEN)
            self.switch_buttons.append(btn)

    def _log_event(self, ev):
        """Log a battle event without animation queue (for instant display)."""
        t = ev.get("type", "")
        if t == "weather":
            self.log.add(f"The weather changed to {ev['weather']}!", C_ACCENT)
        elif t == "ability_announce":
            self.log.add(f"{ev['pokemon']}'s {ev['ability']}!", C_YELLOW)
        elif t == "hazard_damage":
            self.log.add(f"{ev['target']} was hurt by {ev['hazard']}! ({ev['damage']} dmg)", C_RED)
        elif t == "status_inflict":
            self.log.add(f"{ev['target']} was afflicted with {ev['status']}!", C_YELLOW)
        elif t == "hazard_clear":
            self.log.add(f"{ev['target']} absorbed the hazards!", C_GREEN)
        elif t == "faint":
            self.log.add(f"{ev['target']} fainted!", C_RED)

    def _select_move(self, move_name):
        if self.phase != "choose_move":
            return
        self.phase = "animating"
        bs = self.battle_state
        enemy_move = ai_choose_move(self.enemy_poke, self.player_poke, bs)

        # Determine turn order using full speed/priority system
        first, second = determine_turn_order(
            self.player_poke, self.enemy_poke, move_name, enemy_move, bs
        )
        if first == "player":
            turns = [
                (self.player_poke, self.enemy_poke, move_name, "player", 0),
                (self.enemy_poke, self.player_poke, enemy_move, "enemy", 1),
            ]
        else:
            turns = [
                (self.enemy_poke, self.player_poke, enemy_move, "enemy", 1),
                (self.player_poke, self.enemy_poke, move_name, "player", 0),
            ]

        # Collect all events
        all_events = []
        for atk, dfn, move, side, atk_side in turns:
            if atk.is_fainted():
                break
            events = execute_move(atk, dfn, move, bs, atk_side)
            for ev in events:
                ev["side"] = side
            all_events.extend(events)
            # If defender fainted, handle switching
            if dfn.is_fainted():
                if side == "player":
                    next_poke = self.enemy_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "send_out", "side": "enemy",
                                           "trainer": self.enemy_trainer.name,
                                           "species": next_poke.species})
                    else:
                        all_events.append({"type": "battle_end", "winner": "player"})
                else:
                    next_poke = self.player_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "need_switch", "side": "player"})
                    else:
                        all_events.append({"type": "battle_end", "winner": "enemy"})
                break
            # If attacker fainted (recoil, Life Orb, etc.)
            if atk.is_fainted():
                if side == "player":
                    next_poke = self.player_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "need_switch", "side": "player"})
                    else:
                        all_events.append({"type": "battle_end", "winner": "enemy"})
                else:
                    next_poke = self.enemy_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "send_out", "side": "enemy",
                                           "trainer": self.enemy_trainer.name,
                                           "species": next_poke.species})
                    else:
                        all_events.append({"type": "battle_end", "winner": "player"})
                break

        # End-of-turn effects (weather damage, status damage, Leftovers, etc.)
        if self.result is None and not self.player_poke.is_fainted() and not self.enemy_poke.is_fainted():
            eot_events = do_turn_end_effects(self.player_poke, self.enemy_poke, bs)
            for ev in eot_events:
                if ev.get("target") == self.player_poke.species:
                    ev["side"] = "player"
                else:
                    ev["side"] = "enemy"
            all_events.extend(eot_events)
            # Check for faints from end-of-turn
            for poke, side_name, trainer in [
                (self.player_poke, "player", self.player_trainer),
                (self.enemy_poke, "enemy", self.enemy_trainer),
            ]:
                if poke.is_fainted():
                    if side_name == "player":
                        next_p = trainer.first_available()
                        if next_p:
                            all_events.append({"type": "need_switch", "side": "player"})
                        else:
                            all_events.append({"type": "battle_end", "winner": "enemy"})
                    else:
                        next_p = trainer.first_available()
                        if next_p:
                            all_events.append({"type": "send_out", "side": "enemy",
                                               "trainer": self.enemy_trainer.name,
                                               "species": next_p.species})
                        else:
                            all_events.append({"type": "battle_end", "winner": "player"})

        self.anim_events = all_events
        self.anim_timer = 0

    def _switch_to(self, poke):
        self.player_poke = poke
        poke.reset_battle_state()
        self.log.add(f"Go, {poke.species}!", C_GREEN)
        # Apply switch-in effects (hazards, abilities)
        sin_events = do_switch_in_effects(poke, 0, self.battle_state)
        for ev in sin_events:
            self._log_event(ev)
        # Intimidate
        if poke.ability == "Intimidate" and not self.enemy_poke.is_fainted():
            actual = self.enemy_poke.change_stat("atk", -1)
            if actual:
                self.log.add(f"{self.enemy_poke.species}'s Attack fell! (Intimidate)", C_YELLOW)
        if poke.is_fainted():
            # Died from hazards
            next_p = self.player_trainer.first_available()
            if next_p:
                self.phase = "switch"
                self._build_switch_buttons()
                return
            else:
                self.result = False
                self.phase = "done"
                self.log.add("You lost the battle...", C_RED)
                self._build_done_button()
                return
        self.phase = "choose_move"
        self._build_move_buttons()

    def _process_next_event(self):
        if not self.anim_events:
            if self.result is not None:
                self.phase = "done"
                self._build_done_button()
            else:
                self.phase = "choose_move"
                self._build_move_buttons()
            return

        ev = self.anim_events.pop(0)
        t = ev["type"]

        if t == "use_move":
            mcolor = type_color(ev.get("move_type", "Normal"))
            self.log.add(f"{ev['user']} used {ev['move']}!", mcolor)
        elif t == "miss":
            self.log.add("It missed!", C_TEXT_DIM)
        elif t == "immune":
            self.log.add(f"It doesn't affect {ev['target']}...", C_TEXT_DIM)
        elif t == "effective":
            if ev["multiplier"] >= 2.0:
                self.log.add("It's super effective!", C_GREEN)
            else:
                self.log.add("It's not very effective...", C_TEXT_DIM)
        elif t == "critical_hit":
            self.log.add("A critical hit!", C_GOLD)
        elif t == "damage":
            self.log.add(f"{ev['target']} took {ev['damage']} damage! ({ev['hp']}/{ev['max_hp']} HP)", C_RED)
        elif t == "faint":
            self.log.add(f"{ev['target']} fainted!", C_RED)
        elif t == "send_out":
            old_enemy = self.enemy_poke
            self.enemy_poke = self.enemy_trainer.first_available()
            if self.enemy_poke:
                self.enemy_poke.reset_battle_state()
                self.log.add(f"{ev['trainer']} sends out {ev['species']}!", C_RED)
                # Switch-in effects for new enemy
                sin = do_switch_in_effects(self.enemy_poke, 1, self.battle_state)
                for sev in sin:
                    self._log_event(sev)
                if self.enemy_poke.ability == "Intimidate" and not self.player_poke.is_fainted():
                    actual = self.player_poke.change_stat("atk", -1)
                    if actual:
                        self.log.add(f"{self.player_poke.species}'s Attack fell! (Intimidate)", C_YELLOW)
        elif t == "need_switch":
            available = [(i, p) for i, p in enumerate(self.player_trainer.team) if not p.is_fainted()]
            if len(available) == 1:
                self._switch_to(available[0][1])
                self.anim_events.clear()
                return
            else:
                self.phase = "switch"
                self._build_switch_buttons()
                self.anim_events.clear()
                return
        elif t == "battle_end":
            self.result = (ev["winner"] == "player")
            if self.result:
                self.log.add("You won the battle!", C_GOLD)
            else:
                self.log.add("You lost the battle...", C_RED)
        elif t == "fail":
            self.log.add(f"{ev['user']} tried to use {ev['move']}, but it failed!", C_TEXT_DIM)
        # ── New event types ──
        elif t == "status_inflict":
            self.log.add(f"{ev['target']} was afflicted with {ev['status']}!", C_YELLOW)
        elif t == "status_cure":
            self.log.add(f"{ev['target']} was cured of {ev['status']}!", C_GREEN)
        elif t == "status_immobile":
            status_msgs = {
                "sleep": f"{ev['target']} is fast asleep!",
                "freeze": f"{ev['target']} is frozen solid!",
                "paralysis": f"{ev['target']} is paralyzed! It can't move!",
                "flinch": f"{ev['target']} flinched!",
                "infatuation": f"{ev['target']} is immobilized by love!",
            }
            self.log.add(status_msgs.get(ev["status"], f"{ev['target']} can't move!"), C_YELLOW)
        elif t == "status_damage":
            self.log.add(f"{ev['target']} was hurt by {ev['status']}! ({ev['damage']} dmg)", C_RED)
        elif t == "confusion_hit":
            self.log.add(f"{ev['target']} hurt itself in confusion! ({ev['damage']} dmg)", C_YELLOW)
        elif t == "stat_change":
            direction = "rose" if ev["amount"] > 0 else "fell"
            sharply = "sharply " if abs(ev["amount"]) >= 2 else ""
            self.log.add(f"{ev['target']}'s {ev['stat']} {sharply}{direction}!", C_ACCENT)
        elif t == "recoil":
            self.log.add(f"{ev['target']} was hurt by recoil! ({ev['damage']} dmg)", C_RED)
        elif t == "drain":
            self.log.add(f"{ev['target']} restored {ev['amount']} HP!", C_GREEN)
        elif t == "heal":
            self.log.add(f"{ev['target']} restored HP! ({ev['hp']}/{ev['max_hp']})", C_GREEN)
        elif t == "protect":
            self.log.add(f"{ev['target']} protected itself!", C_GREEN)
        elif t == "protected":
            self.log.add(f"{ev['target']} protected itself!", C_GREEN)
        elif t == "substitute":
            self.log.add(f"{ev['target']} created a substitute!", C_ACCENT)
        elif t == "weather":
            self.log.add(f"The weather changed to {ev['weather']}!", C_ACCENT)
        elif t == "weather_end":
            self.log.add(f"The {ev['weather']} subsided!", C_TEXT_DIM)
        elif t == "weather_damage":
            self.log.add(f"{ev['target']} was buffeted by {ev['weather']}! ({ev['damage']} dmg)", C_RED)
        elif t == "hazard_set":
            self.log.add(f"{ev['hazard']} was set up!", C_ACCENT)
        elif t == "hazard_damage":
            self.log.add(f"{ev['target']} was hurt by {ev['hazard']}! ({ev['damage']} dmg)", C_RED)
        elif t == "hazard_clear":
            self.log.add(f"The hazards were cleared!", C_GREEN)
        elif t == "screen_set":
            self.log.add(f"{ev['screen']} was set up!", C_ACCENT)
        elif t == "screen_end":
            self.log.add(f"The {ev['screen']} wore off!", C_TEXT_DIM)
        elif t == "tailwind":
            self.log.add("Tailwind blew from behind!", C_ACCENT)
        elif t == "tailwind_end":
            self.log.add("The tailwind died down!", C_TEXT_DIM)
        elif t == "leech_seed":
            self.log.add(f"{ev['target']}'s health was sapped by Leech Seed! ({ev['damage']} dmg)", C_RED)
        elif t == "curse_damage":
            self.log.add(f"{ev['target']} was afflicted by the curse! ({ev['damage']} dmg)", C_RED)
        elif t == "curse_ghost":
            self.log.add(f"{ev['user']} cut its own HP to lay a curse on {ev['target']}!", C_RED)
        elif t == "item_heal":
            self.log.add(f"{ev['target']} restored HP with {ev['item']}! (+{ev['amount']})", C_GREEN)
        elif t == "item_damage":
            self.log.add(f"{ev['target']} was hurt by {ev['item']}! ({ev['damage']} dmg)", C_RED)
        elif t == "ability_heal":
            self.log.add(f"{ev['target']} healed with {ev['ability']}! (+{ev['amount']})", C_GREEN)
        elif t == "ability_cure":
            self.log.add(f"{ev['target']}'s {ev['ability']} cured its {ev['status']}!", C_GREEN)
        elif t == "ability_stat":
            self.log.add(f"{ev['target']}'s {ev['ability']} raised its {ev['stat']}!", C_ACCENT)
        elif t == "ability_end":
            self.log.add(f"{ev['target']}'s {ev['ability']} wore off!", C_TEXT_DIM)
        elif t == "ability_immune":
            self.log.add(f"{ev['target']}'s {ev['ability']} nullified the attack!", C_GREEN)
        elif t == "ability_contact_damage":
            self.log.add(f"{ev['target']} was hurt by {ev['ability']}! ({ev['damage']} dmg)", C_RED)
        elif t == "ability_status":
            self.log.add(f"{ev['target']} was afflicted by {ev['ability']}! ({ev['status']})", C_YELLOW)
        elif t == "ability_announce":
            self.log.add(f"{ev['pokemon']}'s {ev['ability']}!", C_YELLOW)
        elif t == "field_set":
            self.log.add(f"{ev['effect']} twisted the dimensions!", C_ACCENT)
        elif t == "field_end":
            self.log.add(f"{ev['effect']} wore off!", C_TEXT_DIM)
        elif t == "haze":
            self.log.add("All stat changes were reset!", C_ACCENT)
        elif t == "belly_drum":
            self.log.add(f"{ev['target']} cut its HP and maxed its Attack!", C_GOLD)
        elif t == "nightmare_damage":
            self.log.add(f"{ev['target']} was hurt by Nightmare! ({ev['damage']} dmg)", C_RED)

    def _build_done_button(self):
        label = "Victory! Continue..." if self.result else "Defeat... Continue..."
        color = C_GREEN if self.result else C_RED
        self.done_button = Button(label, SCREEN_W // 2 - 120, 680, 240, 44,
                                  callback=self._finish, font_size=18,
                                  border_color=color)

    def _finish(self):
        s = self.state
        is_champion_fight = (self.player_trainer is s.champion)

        # Fully cure all league Pokemon after every battle
        for member in s.league:
            member.heal_all()
        if s.current_challenger:
            s.current_challenger.heal_all()

        if self.result:
            reward = 50 + s.challenger_position * 25
            s.money += reward
            s.challengers_beaten += 1
            s.current_challenger = None
            s.challenger_position = 0
            s.day += 1
            self.engine.set_scene(ResultScene(s, True, reward))
        else:
            if is_champion_fight:
                self.engine.set_scene(GameOverScene(s))
            else:
                income = 30
                s.money += income
                s.challenger_position += 1
                s.day += 1
                self.engine.set_scene(ResultScene(s, False, income))

    def handle_events(self, events):
        for e in events:
            if self.phase == "choose_move":
                for btn in self.move_buttons:
                    btn.handle_event(e)
            elif self.phase == "switch":
                for btn in self.switch_buttons:
                    btn.handle_event(e)
            elif self.phase == "done" and self.done_button:
                self.done_button.handle_event(e)

    def update(self, dt):
        if self.phase == "animating":
            self.anim_timer += dt
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self._process_next_event()

    def draw(self, screen):
        screen.fill(C_BG)

        # Battle field - top area
        draw_text(screen, self.engine,
                  f"{self.player_trainer.display_name()}  vs  {self.enemy_trainer.display_name()}",
                  SCREEN_W // 2, 15, 20, C_ACCENT, anchor="midtop")

        # Player Pokemon (left)
        if self.player_poke:
            player_panel = Panel(20, 50, SCREEN_W // 2 - 30, 160, title="YOUR POKEMON",
                                 border=C_GREEN, title_color=C_GREEN)
            player_panel.draw(screen, self.engine)
            draw_text(screen, self.engine, f"{self.player_poke.species}  Lv.{self.player_poke.level}",
                      40, 78, 24, C_TEXT_BRIGHT)
            draw_type_badges(screen, self.engine, self.player_poke.types, 40, 110)
            hp = HPBar(40, 140, SCREEN_W // 2 - 90, 24,
                       self.player_poke.current_hp, self.player_poke.max_hp)
            hp.draw(screen, self.engine)

            # Stats
            p = self.player_poke
            draw_text(screen, self.engine,
                      f"ATK:{p.atk}  DEF:{p.defense}  SPA:{p.spa}  SPD:{p.spd}  SPE:{p.spe}",
                      40, 170, 12, C_TEXT_DIM)
            # Status condition
            if p.status1 != Status1.NONE:
                status_colors = {
                    Status1.BURNED: C_RED, Status1.POISONED: (160, 80, 200),
                    Status1.BADLY_POISONED: (160, 80, 200), Status1.PARALYZED: C_YELLOW,
                    Status1.ASLEEP: C_TEXT_DIM, Status1.FROZEN: (100, 200, 255),
                }
                sc = status_colors.get(p.status1, C_YELLOW)
                draw_text(screen, self.engine, p.status1.name[:3], 40, 185, 14, sc)

        # Enemy Pokemon (right)
        if self.enemy_poke:
            ex = SCREEN_W // 2 + 10
            enemy_panel = Panel(ex, 50, SCREEN_W // 2 - 30, 160, title="FOE POKEMON",
                                border=C_RED, title_color=C_RED)
            enemy_panel.draw(screen, self.engine)
            draw_text(screen, self.engine, f"{self.enemy_poke.species}  Lv.{self.enemy_poke.level}",
                      ex + 20, 78, 24, C_TEXT_BRIGHT)
            draw_type_badges(screen, self.engine, self.enemy_poke.types, ex + 20, 110)
            hp = HPBar(ex + 20, 140, SCREEN_W // 2 - 90, 24,
                       self.enemy_poke.current_hp, self.enemy_poke.max_hp)
            hp.draw(screen, self.engine)

            ep = self.enemy_poke
            draw_text(screen, self.engine,
                      f"ATK:{ep.atk}  DEF:{ep.defense}  SPA:{ep.spa}  SPD:{ep.spd}  SPE:{ep.spe}",
                      ex + 20, 170, 12, C_TEXT_DIM)
            # Status condition
            if ep.status1 != Status1.NONE:
                status_colors = {
                    Status1.BURNED: C_RED, Status1.POISONED: (160, 80, 200),
                    Status1.BADLY_POISONED: (160, 80, 200), Status1.PARALYZED: C_YELLOW,
                    Status1.ASLEEP: C_TEXT_DIM, Status1.FROZEN: (100, 200, 255),
                }
                sc = status_colors.get(ep.status1, C_YELLOW)
                draw_text(screen, self.engine, ep.status1.name[:3], ex + 20, 185, 14, sc)

        # Weather indicator
        if self.battle_state.weather != Weather.NONE:
            weather_labels = {
                Weather.HARSH_SUNLIGHT: ("Harsh Sunlight", C_YELLOW),
                Weather.RAIN: ("Rain", (100, 150, 255)),
                Weather.SANDSTORM: ("Sandstorm", (200, 180, 120)),
                Weather.HAILSTORM: ("Hailstorm", (180, 220, 255)),
            }
            wl, wc = weather_labels.get(self.battle_state.weather, ("???", C_TEXT_DIM))
            draw_text(screen, self.engine, f"Weather: {wl}", SCREEN_W // 2, 38, 14, wc, anchor="midtop")

        # Team bars
        self._draw_team_bar(screen, self.player_trainer, 20, 220, "YOUR TEAM")
        self._draw_team_bar(screen, self.enemy_trainer, SCREEN_W // 2 + 10, 220, "FOE TEAM")

        # Sprite placeholder areas
        pygame.draw.rect(screen, C_BG_LIGHT, (130, 300, 150, 150), border_radius=12)
        draw_text(screen, self.engine, self.player_poke.species if self.player_poke else "?",
                  205, 370, 16, C_TEXT_DIM, anchor="center")
        pygame.draw.rect(screen, C_BG_LIGHT, (SCREEN_W - 280, 300, 150, 150), border_radius=12)
        draw_text(screen, self.engine, self.enemy_poke.species if self.enemy_poke else "?",
                  SCREEN_W - 205, 370, 16, C_TEXT_DIM, anchor="center")

        # Message log
        self.log.draw(screen, self.engine)

        # Move buttons / switch buttons / done button
        if self.phase == "choose_move":
            for btn in self.move_buttons:
                btn.draw(screen, self.engine)
        elif self.phase == "switch":
            draw_text(screen, self.engine, "Choose your next Pokemon:",
                      SCREEN_W // 2, 600, 20, C_ACCENT, anchor="midtop")
            for btn in self.switch_buttons:
                btn.draw(screen, self.engine)
        elif self.phase == "done" and self.done_button:
            self.done_button.draw(screen, self.engine)
        elif self.phase == "animating":
            draw_text(screen, self.engine, "...", SCREEN_W // 2, 660, 24, C_TEXT_DIM, anchor="center")

    def _draw_team_bar(self, screen, trainer, x, y, label):
        """Draw a compact team health summary."""
        draw_text(screen, self.engine, label, x, y, 12, C_TEXT_DIM)
        for i, p in enumerate(trainer.team):
            bx = x + i * 78
            by = y + 18
            if p.is_fainted():
                color = (80, 30, 30)
                border = C_RED
            else:
                ratio = p.current_hp / p.max_hp
                color = (30, 60, 40) if ratio > 0.5 else (60, 50, 20)
                border = C_GREEN if ratio > 0.5 else C_YELLOW
            pygame.draw.rect(screen, color, (bx, by, 72, 28), border_radius=4)
            pygame.draw.rect(screen, border, (bx, by, 72, 28), 1, border_radius=4)
            draw_text(screen, self.engine, p.species[:8], bx + 36, by + 4, 11,
                      C_TEXT_BRIGHT, anchor="midtop")
            draw_text(screen, self.engine,
                      "KO" if p.is_fainted() else f"{p.current_hp}/{p.max_hp}",
                      bx + 36, by + 16, 10,
                      C_RED if p.is_fainted() else C_TEXT_DIM, anchor="midtop")


# ─── Result Scene (post-battle) ─────────────────────────────────────

class ResultScene(Scene):
    """Shows battle result and transitions to next day."""

    def __init__(self, state, won, reward):
        super().__init__()
        self.state = state
        self.won = won
        self.reward = reward
        self.btn = Button("Continue", SCREEN_W // 2 - 80, 500, 160, 44,
                          callback=self._continue, font_size=20,
                          border_color=C_GREEN if won else C_YELLOW)

    def _continue(self):
        self.engine.set_scene(DayScene(self.state))

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)

    def draw(self, screen):
        screen.fill(C_BG)
        s = self.state

        if self.won:
            draw_text(screen, self.engine, "VICTORY!", SCREEN_W // 2, 180, 48, C_GOLD, anchor="center")
            draw_text(screen, self.engine, "The challenger has been defeated!",
                      SCREEN_W // 2, 250, 22, C_GREEN, anchor="center")
        else:
            draw_text(screen, self.engine, "DEFEAT", SCREEN_W // 2, 180, 48, C_RED, anchor="center")
            draw_text(screen, self.engine, "The challenger advances!",
                      SCREEN_W // 2, 250, 22, C_YELLOW, anchor="center")
            remaining = len(s.league) - s.challenger_position
            if remaining <= 2:
                draw_text(screen, self.engine,
                          f"WARNING: {remaining} stage(s) from YOU!",
                          SCREEN_W // 2, 290, 20, C_RED, anchor="center")

        draw_text(screen, self.engine, f"+${self.reward}",
                  SCREEN_W // 2, 350, 32, C_YELLOW, anchor="center")
        draw_text(screen, self.engine, f"Total: ${s.money}",
                  SCREEN_W // 2, 400, 20, C_TEXT_DIM, anchor="center")

        self.btn.draw(screen, self.engine)


# ─── Shop Scene ─────────────────────────────────────────────────────

class ShopScene(Scene):
    """Shop for upgrades — tier-based system."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.phase = "main"
        self.buttons = []
        self.sub_buttons = []
        self.message = ""
        self.message_timer = 0
        self.message_color = C_TEXT
        self.selected_member = None
        self.selected_poke = None
        self._build_main()

    def _build_main(self):
        self.phase = "main"
        bx = SCREEN_W // 2 - 150
        self.buttons = [
            Button("Upgrade League Member", bx, 300, 300, 42,
                   callback=self._pick_member_start,
                   font_size=17, border_color=C_ACCENT),
            Button("View Teams", bx, 360, 300, 42,
                   callback=lambda: self._start_action("view_teams"),
                   font_size=17),
            Button("Back", bx, 430, 300, 42,
                   callback=self._back, font_size=17,
                   color=(60, 40, 40), hover_color=(80, 50, 50),
                   border_color=C_RED),
        ]
        self.sub_buttons = []

    def _start_action(self, action):
        if action == "view_teams":
            self.phase = "view_teams"
            self.sub_buttons = [
                Button("Back", SCREEN_W // 2 - 60, SCREEN_H - 60, 120, 40,
                       callback=self._build_main, font_size=16, border_color=C_ACCENT),
            ]

    def _pick_member_start(self):
        self.phase = "pick_member"
        self.sub_buttons = []
        for i, member in enumerate(self.state.league):
            label = f"{member.display_name()} ({len(member.team)} Pokemon)"
            btn = Button(label, SCREEN_W // 2 - 180, 200 + i * 48, 360, 40,
                         callback=lambda m=member: self._pick_member(m),
                         font_size=16, border_color=C_ACCENT)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 200 + len(self.state.league) * 48 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _pick_member(self, member):
        self.selected_member = member
        is_champion = (member is self.state.champion)
        if is_champion:
            # Champion can only level up
            self.phase = "champion_actions"
            self._build_champion_actions(member)
        else:
            # Non-champion gets tier upgrades
            self.phase = "member_actions"
            self._build_member_actions(member)

    def _build_champion_actions(self, member):
        self.sub_buttons = []
        for i, p in enumerate(member.team):
            cost = 50
            label = f"Level Up {p.species} Lv.{p.level} → {p.level + 1}  (${cost})"
            btn = Button(label, SCREEN_W // 2 - 220, 220 + i * 48, 440, 40,
                         callback=lambda poke=p: self._do_champion_levelup(poke),
                         font_size=15, border_color=C_GREEN)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 220 + len(member.team) * 48 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _do_champion_levelup(self, poke):
        if self.state.money < 50:
            self._show_message("Not enough money! Need $50.", C_RED)
            return
        poke.level_up(1)
        self.state.money -= 50
        self._show_message(f"{poke.species} leveled up to Lv.{poke.level}! (-$50)", C_GREEN)
        self._build_champion_actions(self.selected_member)

    def _build_member_actions(self, member):
        self.sub_buttons = []
        bx = SCREEN_W // 2 - 150
        # Upgrade Pokemon
        next_species = member.get_next_tier_pokemon()
        if next_species:
            pdata = POKEMON_DB[next_species]
            types_str = "/".join(pdata["types"])
            pre_evo = EVOLVES_FROM.get(next_species)
            action_desc = f"evolves {pre_evo}" if pre_evo and any(p.species == pre_evo for p in member.team) else "adds to team"
            label = f"Upgrade Pokemon: {next_species} [{types_str}] ({action_desc})  ($200)"
            self.sub_buttons.append(
                Button(label, bx - 70, 220, 440, 42,
                       callback=lambda: self._do_upgrade_pokemon(member, next_species),
                       font_size=15, border_color=C_ACCENT)
            )
        else:
            self.sub_buttons.append(
                Button("Pokemon: MAX TIER", bx - 70, 220, 440, 42,
                       font_size=15, border_color=C_TEXT_DIM,
                       color=(40, 40, 40), hover_color=(40, 40, 40))
            )

        # Upgrade Move — pick a Pokemon first
        self.sub_buttons.append(
            Button("Upgrade Move  ($100)", bx - 70, 270, 440, 42,
                   callback=lambda: self._pick_poke_for_move(member),
                   font_size=15, border_color=C_ACCENT)
        )

        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 330, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _do_upgrade_pokemon(self, member, species):
        if self.state.money < 200:
            self._show_message("Not enough money! Need $200.", C_RED)
            return
        avg_level = sum(p.level for p in member.team) // len(member.team) if member.team else 10
        new_level = max(5, avg_level)
        member.add_tier_pokemon(species, new_level)
        self.state.money -= 200
        self._show_message(f"{species} Lv.{new_level} joined {member.display_name()}'s team! (-$200)", C_GREEN)
        self._build_member_actions(member)

    def _pick_poke_for_move(self, member):
        if self.state.money < 100:
            self._show_message("Not enough money! Need $100.", C_RED)
            return
        self.phase = "pick_poke_move"
        self.sub_buttons = []
        for i, p in enumerate(member.team):
            label = f"{p.species} Lv.{p.level}  ({', '.join(p.moves)})"
            btn = Button(label, SCREEN_W // 2 - 220, 220 + i * 48, 440, 40,
                         callback=lambda poke=p: self._show_move_upgrades(poke),
                         font_size=15, border_color=C_ACCENT)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 220 + len(member.team) * 48 + 10, 120, 36,
                   callback=lambda: self._build_member_actions(member), font_size=14, border_color=C_RED)
        )

    def _show_move_upgrades(self, poke):
        self.selected_poke = poke
        self.phase = "pick_move_upgrade"
        self.sub_buttons = []
        row = 0

        # Existing type upgrades
        for mtype, cur_tier, max_tier in poke.get_available_move_upgrades():
            tier_list = poke.move_tiers[mtype]
            cur_move = tier_list[cur_tier - 1]
            next_move = tier_list[cur_tier]
            label = f"{mtype}: {cur_move} → {next_move}  ($100)"
            mcolor = type_color(mtype)
            r, g, b = mcolor
            btn = Button(label, SCREEN_W // 2 - 220, 220 + row * 44, 440, 38,
                         callback=lambda mt=mtype: self._do_move_upgrade(poke, mt),
                         font_size=15, color=(r // 5 + 20, g // 5 + 20, b // 5 + 20),
                         hover_color=(r // 4 + 30, g // 4 + 30, b // 4 + 30),
                         border_color=mcolor)
            self.sub_buttons.append(btn)
            row += 1

        # New types to learn
        for mtype in poke.get_learnable_new_types():
            tier_list = poke.move_tiers[mtype]
            first_move = tier_list[0]
            label = f"Learn {mtype}: {first_move}  ($100)"
            mcolor = type_color(mtype)
            r, g, b = mcolor
            btn = Button(label, SCREEN_W // 2 - 220, 220 + row * 44, 440, 38,
                         callback=lambda mt=mtype: self._do_move_upgrade(poke, mt),
                         font_size=15, color=(r // 5 + 20, g // 5 + 20, b // 5 + 20),
                         hover_color=(r // 4 + 30, g // 4 + 30, b // 4 + 30),
                         border_color=mcolor)
            self.sub_buttons.append(btn)
            row += 1

        if row == 0:
            self._show_message(f"{poke.species} has all moves maxed!", C_YELLOW)
            self._build_member_actions(self.selected_member)
            return

        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 220 + row * 44 + 10, 120, 36,
                   callback=lambda: self._build_member_actions(self.selected_member),
                   font_size=14, border_color=C_RED)
        )

    def _do_move_upgrade(self, poke, move_type):
        if self.state.money < 100:
            self._show_message("Not enough money! Need $100.", C_RED)
            return
        new_move = poke.upgrade_move_type(move_type)
        if new_move:
            self.state.money -= 100
            self._show_message(f"{poke.species} learned {new_move}! (-$100)", C_GREEN)
        self._build_member_actions(self.selected_member)

    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    def _back(self):
        self.engine.set_scene(DayScene(self.state))

    def handle_events(self, events):
        for e in events:
            if self.phase == "main":
                for btn in self.buttons:
                    btn.handle_event(e)
            else:
                for btn in self.sub_buttons:
                    btn.handle_event(e)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, screen):
        screen.fill(C_BG)

        draw_text(screen, self.engine, "POKEMON LEAGUE SHOP",
                  SCREEN_W // 2, 30, 32, C_GOLD, anchor="midtop")
        draw_text(screen, self.engine, f"${self.state.money}",
                  SCREEN_W // 2, 70, 24, C_YELLOW, anchor="midtop")

        if self.message:
            draw_text(screen, self.engine, self.message,
                      SCREEN_W // 2, 110, 18, self.message_color, anchor="midtop")

        if self.phase == "main":
            for btn in self.buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "view_teams":
            y = 140
            for member in self.state.league:
                draw_text(screen, self.engine, member.display_name(), 60, y, 18, C_ACCENT)
                y += 24
                for p in member.team:
                    types_str = "/".join(p.types)
                    moves_str = ", ".join(p.moves)
                    draw_text(screen, self.engine,
                              f"  {p.species} Lv.{p.level} [{types_str}] - {moves_str}",
                              80, y, 14, C_TEXT)
                    y += 20
                y += 6
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "champion_actions":
            draw_text(screen, self.engine,
                      f"{self.selected_member.display_name()} — Level Up (+1 Lv, $50 each)",
                      SCREEN_W // 2, 170, 20, C_ACCENT, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "member_actions":
            draw_text(screen, self.engine,
                      f"Upgrades for {self.selected_member.display_name()}:",
                      SCREEN_W // 2, 180, 20, C_ACCENT, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase in ("pick_poke_move", "pick_move_upgrade"):
            header = f"Upgrade move for {self.selected_member.display_name()}:"
            if self.phase == "pick_move_upgrade":
                header = f"Pick upgrade for {self.selected_poke.species}:  ($100)"
            draw_text(screen, self.engine, header,
                      SCREEN_W // 2, 180, 20, C_ACCENT, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        else:
            if self.phase == "pick_member":
                draw_text(screen, self.engine, "Choose a League member:",
                          SCREEN_W // 2, 160, 20, C_ACCENT, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)


# ─── League Overview Scene ──────────────────────────────────────────

class LeagueScene(Scene):
    """Display the full league in a graphical overview."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.scroll_y = 0
        self.btn = Button("Back", SCREEN_W // 2 - 60, SCREEN_H - 55, 120, 40,
                          callback=self._back, font_size=16, border_color=C_ACCENT)

    def _back(self):
        self.engine.set_scene(DayScene(self.state))

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)
            if e.type == pygame.MOUSEWHEEL:
                self.scroll_y -= e.y * 30
                self.scroll_y = max(0, self.scroll_y)

    def draw(self, screen):
        screen.fill(C_BG)
        draw_text(screen, self.engine, "LEAGUE OVERVIEW",
                  SCREEN_W // 2, 15, 28, C_GOLD, anchor="midtop")

        y = 60 - self.scroll_y
        for i, member in enumerate(self.state.league):
            is_challenger = (i == self.state.challenger_position and
                             self.state.current_challenger is not None)
            border = C_RED if is_challenger else C_PANEL_BORDER
            panel_h = 30 + len(member.team) * 28
            panel = Panel(40, y, SCREEN_W - 80, panel_h, border=border)
            panel.draw(screen, self.engine)

            marker = "  << CHALLENGER" if is_challenger else ""
            color = C_RED if is_challenger else C_ACCENT
            draw_text(screen, self.engine,
                      f"Stage {i + 1}: {member.display_name()}{marker}",
                      55, y + 6, 18, color)

            for j, p in enumerate(member.team):
                py = y + 30 + j * 28
                draw_text(screen, self.engine, f"{p.species} Lv.{p.level}",
                          75, py, 15, C_TEXT_BRIGHT)
                draw_type_badges(screen, self.engine, p.types, 220, py, 12)
                moves = ", ".join(p.moves)
                draw_text(screen, self.engine, moves, 370, py + 2, 13, C_TEXT_DIM)

            y += panel_h + 8

        self.btn.draw(screen, self.engine)


# ─── Game Over Scene ────────────────────────────────────────────────

class GameOverScene(Scene):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.btn = Button("Exit Game", SCREEN_W // 2 - 80, 500, 160, 44,
                          callback=self._quit, font_size=20, border_color=C_RED)

    def _quit(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)

    def draw(self, screen):
        screen.fill((15, 10, 10))

        draw_text(screen, self.engine, "GAME OVER", SCREEN_W // 2, 180, 56, C_RED, anchor="center")
        draw_text(screen, self.engine, "The Champion has fallen!",
                  SCREEN_W // 2, 260, 24, C_TEXT_DIM, anchor="center")
        draw_text(screen, self.engine, f"You lasted {self.state.day} days",
                  SCREEN_W // 2, 340, 22, C_TEXT, anchor="center")
        draw_text(screen, self.engine, f"Challengers defeated: {self.state.challengers_beaten}",
                  SCREEN_W // 2, 380, 22, C_GOLD, anchor="center")

        self.btn.draw(screen, self.engine)
