"""
Pokemon League Champion - Game Scenes
All Pygame scenes: Title, Day, Battle, Shop, League Overview, GameOver.
"""
import pygame
import sys
from engine import (
    Scene, Panel, Button, Label, TextInput, HPBar, MessageLog,
    SCREEN_W, SCREEN_H, C_BG, C_BG_LIGHT, C_PANEL, C_PANEL_BORDER,
    C_TEXT, C_TEXT_DIM, C_TEXT_BRIGHT, C_ACCENT, C_GOLD, C_GREEN, C_RED,
    C_YELLOW, C_BTN, C_BTN_HOVER, C_BTN_BORDER,
    draw_text, draw_type_badges, draw_pokemon_card, type_color,
)
from pokemon import Trainer, Pokemon
from battle_logic import ai_choose_move, execute_move
from generator import generate_challenger
from data import (
    DEFAULT_GYM_LEADERS, DEFAULT_ELITE_FOUR, CHAMPION_STARTER_OPTIONS,
    POKEMON_DB, MOVES_DB,
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
    """Name entry + team selection."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.phase = "name"  # "name" -> "team"
        self.name_input = TextInput(SCREEN_W // 2 - 150, 380, 300, 44,
                                    placeholder="Enter your name...", font_size=22)
        self.confirm_btn = Button("Confirm", SCREEN_W // 2 - 60, 440, 120, 40,
                                  callback=self._confirm_name, font_size=18)
        self.team_buttons = []

    def _confirm_name(self):
        name = self.name_input.text.strip()
        if name:
            self.state.player_name = name
        else:
            self.state.player_name = "Champion"
        self.phase = "team"
        self._build_team_buttons()

    def _build_team_buttons(self):
        self.team_buttons = []
        for i, option in enumerate(CHAMPION_STARTER_OPTIONS):
            y = 250 + i * 160
            btn = Button(
                f"Choose: {option['label']}",
                SCREEN_W // 2 + 120, y + 50, 180, 40,
                callback=lambda idx=i: self._pick_team(idx),
                font_size=16,
                color=(60, 80, 60), hover_color=(70, 110, 70),
                border_color=C_GREEN,
            )
            self.team_buttons.append((option, btn))

    def _pick_team(self, idx):
        champion_data = CHAMPION_STARTER_OPTIONS[idx]
        # Build league
        gym_leaders = []
        for gl_data in DEFAULT_GYM_LEADERS:
            gym_leaders.append(Trainer(gl_data["name"], gl_data["title"],
                                       gl_data["team"], gl_data.get("specialty")))
        elite_four = []
        for e4_data in DEFAULT_ELITE_FOUR:
            elite_four.append(Trainer(e4_data["name"], e4_data["title"],
                                      e4_data["team"], e4_data.get("specialty")))
        champion = Trainer(self.state.player_name, "Champion", champion_data["team"])
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
            elif self.phase == "team":
                for _, btn in self.team_buttons:
                    btn.handle_event(e)

    def update(self, dt):
        if self.phase == "name":
            self.name_input.update(dt)

    def draw(self, screen):
        screen.fill(C_BG)

        # Title
        draw_text(screen, self.engine, "POKEMON LEAGUE CHAMPION",
                  SCREEN_W // 2, 60, 42, C_GOLD, anchor="midtop")
        draw_text(screen, self.engine, "Defend your title. Manage your League.",
                  SCREEN_W // 2, 115, 18, C_TEXT_DIM, anchor="midtop")

        if self.phase == "name":
            draw_text(screen, self.engine, "What is your name, Champion?",
                      SCREEN_W // 2, 320, 24, C_ACCENT, anchor="midtop")
            self.name_input.draw(screen, self.engine)
            self.confirm_btn.draw(screen, self.engine)

        elif self.phase == "team":
            draw_text(screen, self.engine, f"Welcome, {self.state.player_name}!  Choose your Champion team:",
                      SCREEN_W // 2, 190, 22, C_ACCENT, anchor="midtop")

            for i, (option, btn) in enumerate(self.team_buttons):
                y = 250 + i * 160
                panel = Panel(80, y, SCREEN_W - 160, 145)
                panel.draw(screen, self.engine)

                draw_text(screen, self.engine, option["label"],
                          100, y + 10, 22, C_GOLD)

                for j, pdata in enumerate(option["team"]):
                    py = y + 38 + j * 28
                    draw_text(screen, self.engine,
                              f"{pdata['species']}  Lv.{pdata['level']}",
                              110, py, 16, C_TEXT_BRIGHT)
                    # Moves
                    moves_str = ", ".join(pdata["moves"])
                    draw_text(screen, self.engine, moves_str,
                              280, py, 14, C_TEXT_DIM)

                btn.draw(screen, self.engine)


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

        # Challenger side (left)
        panel_w = (SCREEN_W - 80) // 2 - 10
        chall_panel = Panel(30, 120, panel_w, 420, title="CHALLENGER",
                            border=(180, 60, 60), title_color=C_RED)
        chall_panel.draw(screen, self.engine)

        draw_text(screen, self.engine, challenger.display_name(),
                  50, 148, 20, C_TEXT_BRIGHT)
        draw_text(screen, self.engine,
                  f"Stage {s.challenger_position + 1}/{len(s.league)}",
                  50, 172, 14, C_TEXT_DIM)

        cy = 200
        for p in challenger.team:
            h = draw_pokemon_card(screen, self.engine, p, 45, cy, panel_w - 40, show_moves=True)
            cy += h + 6

        # Defender side (right)
        def_x = SCREEN_W // 2 + 10
        def_panel = Panel(def_x, 120, panel_w, 420, title="DEFENDER",
                          border=(60, 140, 80), title_color=C_GREEN)
        def_panel.draw(screen, self.engine)

        draw_text(screen, self.engine, member.display_name(),
                  def_x + 20, 148, 20, C_TEXT_BRIGHT)

        dy = 200
        for p in member.team:
            h = draw_pokemon_card(screen, self.engine, p, def_x + 15, dy, panel_w - 40, show_moves=True)
            dy += h + 6

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
        self._build_move_buttons()
        self.log.add(f"{player_trainer.name} sends out {self.player_poke.species}!", C_GREEN)
        self.log.add(f"{enemy_trainer.name} sends out {self.enemy_poke.species}!", C_RED)

    def _build_move_buttons(self):
        self.move_buttons = []
        if not self.player_poke or self.player_poke.is_fainted():
            return
        for i, move_name in enumerate(self.player_poke.moves):
            md = MOVES_DB.get(move_name, {})
            mtype = md.get("type", "Normal")
            mcolor = type_color(mtype)
            cat = "PHY" if md.get("category") == "physical" else "SPE"
            label = f"{move_name}  ({mtype} {cat} P:{md.get('power', '?')})"

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

    def _select_move(self, move_name):
        if self.phase != "choose_move":
            return
        self.phase = "animating"
        enemy_move = ai_choose_move(self.enemy_poke, self.player_poke)

        # Determine order
        if self.player_poke.spe >= self.enemy_poke.spe:
            turns = [
                (self.player_poke, self.enemy_poke, move_name, "player"),
                (self.enemy_poke, self.player_poke, enemy_move, "enemy"),
            ]
        else:
            turns = [
                (self.enemy_poke, self.player_poke, enemy_move, "enemy"),
                (self.player_poke, self.enemy_poke, move_name, "player"),
            ]

        # Collect all events
        all_events = []
        for atk, dfn, move, side in turns:
            events = execute_move(atk, dfn, move)
            for ev in events:
                ev["side"] = side
            all_events.extend(events)
            # If defender fainted, handle switching
            if dfn.is_fainted():
                if side == "player":
                    # Enemy fainted
                    next_poke = self.enemy_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "send_out", "side": "enemy",
                                           "trainer": self.enemy_trainer.name,
                                           "species": next_poke.species})
                    else:
                        all_events.append({"type": "battle_end", "winner": "player"})
                else:
                    # Player fainted
                    next_poke = self.player_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "need_switch", "side": "player"})
                    else:
                        all_events.append({"type": "battle_end", "winner": "enemy"})
                break  # Don't let fainted pokemon attack

        self.anim_events = all_events
        self.anim_timer = 0

    def _switch_to(self, poke):
        self.player_poke = poke
        self.log.add(f"Go, {poke.species}!", C_GREEN)
        self.phase = "choose_move"
        self._build_move_buttons()

    def _process_next_event(self):
        if not self.anim_events:
            # Turn done, check state
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
        elif t == "damage":
            self.log.add(f"{ev['target']} took {ev['damage']} damage! ({ev['hp']}/{ev['max_hp']} HP)", C_RED)
        elif t == "faint":
            self.log.add(f"{ev['target']} fainted!", C_RED)
        elif t == "send_out":
            self.enemy_poke = self.enemy_trainer.first_available()
            self.log.add(f"{ev['trainer']} sends out {ev['species']}!", C_RED)
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

    def _build_done_button(self):
        label = "Victory! Continue..." if self.result else "Defeat... Continue..."
        color = C_GREEN if self.result else C_RED
        self.done_button = Button(label, SCREEN_W // 2 - 120, 680, 240, 44,
                                  callback=self._finish, font_size=18,
                                  border_color=color)

    def _finish(self):
        s = self.state
        is_champion_fight = (self.player_trainer is s.champion)

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
    """Shop for upgrades. Sub-phases handle different actions."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.phase = "main"
        self.buttons = []
        self.sub_buttons = []
        self.message = ""
        self.message_timer = 0
        self.message_color = C_TEXT
        self._build_main()

    def _build_main(self):
        self.phase = "main"
        bx = SCREEN_W // 2 - 150
        self.buttons = [
            Button(f"Level Up Pokemon  ($50/lv)", bx, 300, 300, 42,
                   callback=lambda: self._start_action("level_up"),
                   font_size=17, border_color=C_ACCENT),
            Button(f"Teach Move  ($100)", bx, 350, 300, 42,
                   callback=lambda: self._start_action("teach_move"),
                   font_size=17, border_color=C_ACCENT),
            Button(f"Add Pokemon  ($200)", bx, 400, 300, 42,
                   callback=lambda: self._start_action("add_pokemon"),
                   font_size=17, border_color=C_ACCENT),
            Button("View Teams", bx, 460, 300, 42,
                   callback=lambda: self._start_action("view_teams"),
                   font_size=17),
            Button("Back", bx, 530, 300, 42,
                   callback=self._back, font_size=17,
                   color=(60, 40, 40), hover_color=(80, 50, 50),
                   border_color=C_RED),
        ]
        self.sub_buttons = []

    def _start_action(self, action):
        if action == "level_up":
            self.phase = "pick_member_lu"
            self._build_member_buttons("pick_member_lu")
        elif action == "teach_move":
            if self.state.money < 100:
                self._show_message("Not enough money! Need $100.", C_RED)
                return
            self.phase = "pick_member_tm"
            self._build_member_buttons("pick_member_tm")
        elif action == "add_pokemon":
            if self.state.money < 200:
                self._show_message("Not enough money! Need $200.", C_RED)
                return
            self.phase = "pick_member_ap"
            self._build_member_buttons("pick_member_ap")
        elif action == "view_teams":
            self.phase = "view_teams"
            self.sub_buttons = [
                Button("Back", SCREEN_W // 2 - 60, SCREEN_H - 60, 120, 40,
                       callback=self._build_main, font_size=16, border_color=C_ACCENT),
            ]

    def _build_member_buttons(self, next_phase):
        self.sub_buttons = []
        for i, member in enumerate(self.state.league):
            btn = Button(f"{member.display_name()} ({len(member.team)} Pokemon)",
                         SCREEN_W // 2 - 180, 200 + i * 48, 360, 40,
                         callback=lambda m=member, ph=next_phase: self._pick_member(m, ph),
                         font_size=16, border_color=C_ACCENT)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 200 + len(self.state.league) * 48 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _pick_member(self, member, phase):
        self.selected_member = member
        if phase == "pick_member_lu":
            self.phase = "pick_poke_lu"
            self._build_pokemon_buttons(member, "lu")
        elif phase == "pick_member_tm":
            self.phase = "pick_poke_tm"
            self._build_pokemon_buttons(member, "tm")
        elif phase == "pick_member_ap":
            self.phase = "pick_species"
            self._build_species_buttons(member)

    def _build_pokemon_buttons(self, member, action):
        self.sub_buttons = []
        for i, p in enumerate(member.team):
            label = f"{p.species} Lv.{p.level}  ({', '.join(p.moves)})"
            btn = Button(label, SCREEN_W // 2 - 220, 200 + i * 48, 440, 40,
                         callback=lambda poke=p, act=action: self._pick_pokemon(poke, act),
                         font_size=15, border_color=C_ACCENT)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 200 + len(member.team) * 48 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _pick_pokemon(self, poke, action):
        self.selected_poke = poke
        if action == "lu":
            self.phase = "level_up_amount"
            self._build_levelup_buttons(poke)
        elif action == "tm":
            self._build_move_buttons(poke)

    def _build_levelup_buttons(self, poke):
        cost_per = 50
        max_aff = self.state.money // cost_per
        if max_aff == 0:
            self._show_message("Not enough money!", C_RED)
            self._build_main()
            return
        self.sub_buttons = []
        amounts = [1, 2, 3, 5, 10]
        for i, amt in enumerate(amounts):
            if amt > max_aff:
                continue
            cost = amt * cost_per
            btn = Button(f"+{amt} Level{'s' if amt > 1 else ''}  (${cost})",
                         SCREEN_W // 2 - 120, 250 + i * 48, 240, 40,
                         callback=lambda a=amt: self._do_levelup(a),
                         font_size=16, border_color=C_GREEN)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 250 + len(self.sub_buttons) * 48 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _do_levelup(self, levels):
        cost = levels * 50
        self.selected_poke.level_up(levels)
        self.state.money -= cost
        self._show_message(
            f"{self.selected_poke.species} leveled up to Lv.{self.selected_poke.level}! (-${cost})",
            C_GREEN,
        )
        self._build_main()

    def _build_move_buttons(self, poke):
        available = [m for m in poke.learnable_moves if m not in poke.moves]
        if not available:
            self._show_message(f"{poke.species} already knows all moves!", C_YELLOW)
            self._build_main()
            return
        self.phase = "pick_move"
        self.sub_buttons = []
        for i, move_name in enumerate(available):
            md = MOVES_DB[move_name]
            mtype = md["type"]
            cat = "PHY" if md["category"] == "physical" else "SPE"
            label = f"{move_name}  ({mtype} {cat} P:{md['power']} A:{md['accuracy']}%)"
            mcolor = type_color(mtype)
            r, g, b = mcolor
            btn = Button(label, SCREEN_W // 2 - 220, 200 + i * 44, 440, 38,
                         callback=lambda mn=move_name: self._teach_move(mn),
                         font_size=15, color=(r // 5 + 20, g // 5 + 20, b // 5 + 20),
                         hover_color=(r // 4 + 30, g // 4 + 30, b // 4 + 30),
                         border_color=mcolor)
            self.sub_buttons.append(btn)
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, 200 + len(available) * 44 + 10, 120, 36,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _teach_move(self, move_name):
        poke = self.selected_poke
        if len(poke.moves) >= 4:
            self.phase = "replace_move"
            self.new_move = move_name
            self.sub_buttons = []
            for i, m in enumerate(poke.moves):
                md = MOVES_DB[m]
                label = f"Replace: {m} ({md['type']} P:{md['power']})"
                btn = Button(label, SCREEN_W // 2 - 180, 250 + i * 48, 360, 40,
                             callback=lambda idx=i: self._replace_move(idx),
                             font_size=15, border_color=C_YELLOW)
                self.sub_buttons.append(btn)
            self.sub_buttons.append(
                Button("Cancel", SCREEN_W // 2 - 60, 250 + len(poke.moves) * 48 + 10, 120, 36,
                       callback=self._build_main, font_size=14, border_color=C_RED)
            )
        else:
            poke.moves.append(move_name)
            self.state.money -= 100
            self._show_message(f"{poke.species} learned {move_name}! (-$100)", C_GREEN)
            self._build_main()

    def _replace_move(self, idx):
        poke = self.selected_poke
        old_move = poke.moves[idx]
        poke.moves[idx] = self.new_move
        self.state.money -= 100
        self._show_message(f"{poke.species} forgot {old_move}, learned {self.new_move}! (-$100)", C_GREEN)
        self._build_main()

    def _build_species_buttons(self, member):
        current = {p.species for p in member.team}
        available = sorted([s for s in POKEMON_DB if s not in current])
        self.species_list = available
        self.species_page = 0
        self._draw_species_page()

    def _draw_species_page(self):
        self.phase = "pick_species"
        page = self.species_page
        per_page = 10
        start = page * per_page
        end = min(start + per_page, len(self.species_list))
        total_pages = (len(self.species_list) - 1) // per_page + 1

        self.sub_buttons = []
        for i in range(start, end):
            species = self.species_list[i]
            pdata = POKEMON_DB[species]
            types_str = "/".join(pdata["types"])
            r, g, b = type_color(pdata["types"][0])
            btn = Button(f"{species}  [{types_str}]",
                         SCREEN_W // 2 - 180, 180 + (i - start) * 40, 360, 34,
                         callback=lambda s=species: self._add_pokemon(s),
                         font_size=15, color=(r // 5 + 20, g // 5 + 20, b // 5 + 20),
                         hover_color=(r // 4 + 30, g // 4 + 30, b // 4 + 30),
                         border_color=type_color(pdata["types"][0]))
            self.sub_buttons.append(btn)

        nav_y = 180 + (end - start) * 40 + 10
        if page > 0:
            self.sub_buttons.append(
                Button("< Prev", SCREEN_W // 2 - 180, nav_y, 100, 34,
                       callback=self._prev_species_page, font_size=14, border_color=C_ACCENT)
            )
        if end < len(self.species_list):
            self.sub_buttons.append(
                Button("Next >", SCREEN_W // 2 + 80, nav_y, 100, 34,
                       callback=self._next_species_page, font_size=14, border_color=C_ACCENT)
            )
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 60, nav_y + 44, 120, 34,
                   callback=self._build_main, font_size=14, border_color=C_RED)
        )

    def _prev_species_page(self):
        self.species_page = max(0, self.species_page - 1)
        self._draw_species_page()

    def _next_species_page(self):
        self.species_page += 1
        self._draw_species_page()

    def _add_pokemon(self, species):
        member = self.selected_member
        avg_level = sum(p.level for p in member.team) // len(member.team) if member.team else 10
        new_level = max(5, avg_level - 2)
        pdata = POKEMON_DB[species]
        new_poke = Pokemon(species, new_level, pdata["learnable_moves"][:2])

        if len(member.team) >= 6:
            self.new_poke = new_poke
            self.phase = "replace_poke"
            self.sub_buttons = []
            for i, p in enumerate(member.team):
                btn = Button(f"Replace: {p.species} Lv.{p.level}",
                             SCREEN_W // 2 - 160, 250 + i * 48, 320, 40,
                             callback=lambda idx=i: self._do_replace_poke(idx),
                             font_size=15, border_color=C_YELLOW)
                self.sub_buttons.append(btn)
            self.sub_buttons.append(
                Button("Cancel", SCREEN_W // 2 - 60, 250 + 6 * 48 + 10, 120, 36,
                       callback=self._build_main, font_size=14, border_color=C_RED)
            )
        else:
            member.team.append(new_poke)
            self.state.money -= 200
            self._show_message(f"{species} Lv.{new_level} joined the team! (-$200)", C_GREEN)
            self._build_main()

    def _do_replace_poke(self, idx):
        member = self.selected_member
        old = member.team[idx]
        member.team[idx] = self.new_poke
        self.state.money -= 200
        self._show_message(f"{old.species} replaced by {self.new_poke.species}! (-$200)", C_GREEN)
        self._build_main()

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

        # Header
        draw_text(screen, self.engine, "POKEMON LEAGUE SHOP",
                  SCREEN_W // 2, 30, 32, C_GOLD, anchor="midtop")
        draw_text(screen, self.engine, f"${self.state.money}",
                  SCREEN_W // 2, 70, 24, C_YELLOW, anchor="midtop")

        # Message
        if self.message:
            draw_text(screen, self.engine, self.message,
                      SCREEN_W // 2, 110, 18, self.message_color, anchor="midtop")

        # Phase-specific info
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

        elif self.phase == "level_up_amount":
            draw_text(screen, self.engine,
                      f"Level up {self.selected_poke.species} (currently Lv.{self.selected_poke.level})",
                      SCREEN_W // 2, 200, 20, C_ACCENT, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "replace_move":
            draw_text(screen, self.engine,
                      f"Replace which move with {self.new_move}?",
                      SCREEN_W // 2, 200, 20, C_YELLOW, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "replace_poke":
            draw_text(screen, self.engine,
                      f"Team is full. Replace which Pokemon?",
                      SCREEN_W // 2, 200, 20, C_YELLOW, anchor="midtop")
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        else:
            # Generic sub-button phases
            if self.phase.startswith("pick_member"):
                draw_text(screen, self.engine, "Choose a League member:",
                          SCREEN_W // 2, 160, 20, C_ACCENT, anchor="midtop")
            elif self.phase.startswith("pick_poke"):
                draw_text(screen, self.engine,
                          f"Choose a Pokemon from {self.selected_member.display_name()}:",
                          SCREEN_W // 2, 160, 20, C_ACCENT, anchor="midtop")
            elif self.phase == "pick_move":
                draw_text(screen, self.engine,
                          f"Teach which move to {self.selected_poke.species}?  ($100)",
                          SCREEN_W // 2, 160, 20, C_ACCENT, anchor="midtop")
            elif self.phase == "pick_species":
                page = self.species_page
                per_page = 10
                total_pages = (len(self.species_list) - 1) // per_page + 1
                draw_text(screen, self.engine,
                          f"Add a Pokemon to {self.selected_member.display_name()}'s team  ($200)  Page {page+1}/{total_pages}",
                          SCREEN_W // 2, 145, 18, C_ACCENT, anchor="midtop")

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
