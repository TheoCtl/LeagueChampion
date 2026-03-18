"""
Pokemon League Champion - Game Scenes
All Pygame scenes: Title, Day, Battle, Shop, League Overview, GameOver.
Pokemon B/W2 inspired visual style.
"""
import pygame
import sys
import random
from engine import (
    Scene, Panel, Button, Label, TextInput, HPBar, MessageLog,
    SCREEN_W, SCREEN_H, C_BG, C_BG_LIGHT, C_BG_DARK, C_PANEL, C_PANEL_BORDER,
    C_PANEL_HIGHLIGHT, C_TEXT, C_TEXT_DIM, C_TEXT_BRIGHT, C_ACCENT, C_GOLD,
    C_GREEN, C_RED, C_YELLOW, C_CYAN, C_BTN, C_BTN_HOVER, C_BTN_BORDER,
    C_BATTLE_SKY_TOP, C_BATTLE_SKY_BOT, C_BATTLE_GROUND, C_BATTLE_GROUND_DARK,
    C_BATTLE_PLATFORM, C_BATTLE_PLATFORM_SHADOW, C_ACTION_PANEL, C_ACTION_BORDER,
    draw_text, draw_type_badges, draw_pokemon_card, type_color,
    draw_pokemon_sprite, draw_trainer_sprite, draw_pokeball_indicators,
    draw_status_badge, draw_gradient_v, TypeBadge,
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
    DEFAULT_GYM_LEADERS, DEFAULT_ELITE_FOUR, build_trainer_team,
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
        self.phase = "name"
        self.name_input = TextInput(SCREEN_W // 2 - 200, 520, 400, 52,
                                    placeholder="Enter your name...", font_size=24)
        self.confirm_btn = Button("Confirm", SCREEN_W // 2 - 80, 590, 160, 48,
                                  callback=self._confirm_name, font_size=20,
                                  border_color=C_GREEN)
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
            Button(f"Pick {a}", 120, 870, 260, 52,
                   callback=lambda: self._draft_pick(a),
                   font_size=20, color=(35, 55, 35), hover_color=(45, 75, 45),
                   border_color=C_GREEN),
            Button(f"Pick {b}", SCREEN_W - 380, 870, 260, 52,
                   callback=lambda: self._draft_pick(b),
                   font_size=20, color=(35, 55, 35), hover_color=(45, 75, 45),
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
        league_members = []
        for td in DEFAULT_GYM_LEADERS + DEFAULT_ELITE_FOUR:
            team = build_trainer_team(td["specialty"], td["team_count"], td["level"])
            league_members.append(Trainer(td["name"], td["title"],
                                          team, td.get("specialty")))
        champion = Trainer(self.state.player_name, "Champion", team_data)
        self.state.league = league_members + [champion]
        self.state.champion = champion
        from overworld import OverworldScene
        self.engine.set_scene(OverworldScene(self.state))

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
        # Decorative top gradient bar
        draw_gradient_v(screen, (0, 0, SCREEN_W, 120), (30, 40, 70), C_BG)

        draw_text(screen, self.engine, "POKEMON LEAGUE CHAMPION",
                  SCREEN_W // 2, 35, 56, C_GOLD, anchor="midtop", bold=True)
        draw_text(screen, self.engine, "Defend your title. Manage your League.",
                  SCREEN_W // 2, 100, 22, C_TEXT_DIM, anchor="midtop")

        if self.phase == "name":
            # Decorative pokeball-style circle
            pygame.draw.circle(screen, (35, 42, 68), (SCREEN_W // 2, 380), 80, 3)
            pygame.draw.line(screen, (35, 42, 68),
                             (SCREEN_W // 2 - 80, 380), (SCREEN_W // 2 + 80, 380), 2)
            pygame.draw.circle(screen, C_ACCENT, (SCREEN_W // 2, 380), 12)

            draw_text(screen, self.engine, "What is your name, Champion?",
                      SCREEN_W // 2, 440, 28, C_ACCENT, anchor="midtop")
            self.name_input.draw(screen, self.engine)
            self.confirm_btn.draw(screen, self.engine)

        elif self.phase == "draft":
            if self.draft_round < len(self.draft_pairs):
                draw_text(screen, self.engine,
                          f"CHAMPION DRAFT — Round {self.draft_round + 1}/6",
                          SCREEN_W // 2, 140, 32, C_ACCENT, anchor="midtop", bold=True)
                draw_text(screen, self.engine, "Choose one Pokemon from each pair:",
                          SCREEN_W // 2, 180, 18, C_TEXT_DIM, anchor="midtop")

                a, b = self.draft_pairs[self.draft_round]
                self._draw_draft_card(screen, a, 60, 215, SCREEN_W // 2 - 90)
                self._draw_draft_card(screen, b, SCREEN_W // 2 + 30, 215,
                                      SCREEN_W // 2 - 90)

                # "OR" divider with decorative lines
                or_y = 560
                pygame.draw.line(screen, C_PANEL_BORDER,
                                 (SCREEN_W // 2 - 80, or_y),
                                 (SCREEN_W // 2 - 25, or_y), 2)
                draw_text(screen, self.engine, "OR",
                          SCREEN_W // 2, or_y - 10, 32, C_GOLD, anchor="midtop",
                          bold=True)
                pygame.draw.line(screen, C_PANEL_BORDER,
                                 (SCREEN_W // 2 + 25, or_y),
                                 (SCREEN_W // 2 + 80, or_y), 2)

                for btn in self.draft_buttons:
                    btn.draw(screen, self.engine)

            if self.draft_picks:
                draw_text(screen, self.engine, "Your picks:",
                          SCREEN_W // 2, 960, 16, C_TEXT_DIM, anchor="midtop")
                # Draw picked Pokemon as sprites
                total_w = len(self.draft_picks) * 60
                start_x = SCREEN_W // 2 - total_w // 2
                for i, sp in enumerate(self.draft_picks):
                    px = start_x + i * 60
                    draw_pokemon_sprite(screen, self.engine, sp, px, 985, 40)
                    draw_text(screen, self.engine, sp[:6], px + 20, 1030, 11,
                              C_GREEN, anchor="midtop")

    def _draw_draft_card(self, screen, species, x, y, w):
        pdata = POKEMON_DB[species]
        panel = Panel(x, y, w, 620, shadow=True)
        panel.draw(screen, self.engine)

        # Large sprite + name
        draw_pokemon_sprite(screen, self.engine, species, x + 20, y + 15, 72)
        draw_text(screen, self.engine, species, x + 100, y + 18, 30,
                  C_TEXT_BRIGHT, bold=True)
        draw_type_badges(screen, self.engine, pdata["types"], x + 100, y + 55, 15)

        # Stats with visual bars
        stats = pdata["stats"]
        sy = y + 100
        max_stat = 160
        stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
        stat_labels = ["HP", "ATK", "DEF", "SPA", "SPD", "SPE"]
        stat_colors = [
            C_GREEN, (240, 100, 50), (100, 150, 255),
            (170, 80, 240), (100, 200, 100), (255, 180, 60)
        ]
        for i, (sn, sl) in enumerate(zip(stat_names, stat_labels)):
            val = stats[sn]
            draw_text(screen, self.engine, f"{sl}", x + 22, sy, 16, C_TEXT_DIM)
            draw_text(screen, self.engine, str(val), x + 70, sy, 16,
                      C_TEXT_BRIGHT, bold=True)
            # Stat bar
            bar_x = x + 110
            bar_w = w - 140
            bar_h = 14
            pygame.draw.rect(screen, C_BG_DARK, (bar_x, sy + 2, bar_w, bar_h),
                             border_radius=3)
            fill_w = min(bar_w, int(bar_w * val / max_stat))
            if fill_w > 0:
                pygame.draw.rect(screen, stat_colors[i],
                                 (bar_x, sy + 2, fill_w, bar_h), border_radius=3)
            pygame.draw.rect(screen, (50, 55, 80), (bar_x, sy + 2, bar_w, bar_h),
                             1, border_radius=3)
            sy += 24

        # Abilities
        sy += 8
        abilities = pdata.get("abilities", [])
        if abilities:
            draw_text(screen, self.engine, "Abilities:", x + 22, sy, 15, C_ACCENT)
            sy += 22
            for ab in abilities[:3]:
                draw_text(screen, self.engine, f"  • {ab}", x + 22, sy, 14, C_TEXT)
                sy += 20

        # Move tiers
        sy += 8
        draw_text(screen, self.engine, "Move Tiers:", x + 22, sy, 15, C_ACCENT)
        sy += 22
        for mtype, tlist in pdata.get("move_tiers", {}).items():
            mcolor = type_color(mtype)
            pygame.draw.circle(screen, mcolor, (x + 30, sy + 7), 5)
            moves_str = " → ".join(tlist)
            draw_text(screen, self.engine, f" {mtype}: {moves_str}",
                      x + 40, sy, 13, C_TEXT_DIM)
            sy += 18


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
        bx = SCREEN_W // 2 - 160
        self.buttons = [
            Button("Fight!", bx, 850, 320, 50,
                   callback=self._fight, font_size=22,
                   color=(85, 35, 35), hover_color=(125, 45, 45),
                   border_color=C_RED, text_color=C_TEXT_BRIGHT),
            Button("Back", bx, 920, 320, 45,
                   callback=self._go_back, font_size=20,
                   color=(45, 45, 50), hover_color=(55, 55, 65),
                   border_color=C_TEXT_DIM),
        ]

    def _fight(self):
        league_member = self.state.league[self.state.challenger_position]
        league_member.heal_all()
        self.state.current_challenger.heal_all()
        self.engine.set_scene(BattleScene(self.state, league_member,
                                          self.state.current_challenger))

    def _go_back(self):
        from overworld import OverworldScene
        self.engine.set_scene(OverworldScene(self.state))

    def handle_events(self, events):
        for e in events:
            for btn in self.buttons:
                btn.handle_event(e)

    def draw(self, screen):
        screen.fill(C_BG)
        s = self.state

        # Header bar with gradient
        draw_gradient_v(screen, (0, 0, SCREEN_W, 70), (32, 40, 65), C_BG)
        pygame.draw.line(screen, C_PANEL_BORDER, (0, 70), (SCREEN_W, 70), 2)
        draw_text(screen, self.engine, f"DAY {s.day}", 40, 20, 34, C_GOLD, bold=True)
        draw_text(screen, self.engine, f"${s.money}", 280, 28, 24, C_YELLOW, bold=True)
        draw_text(screen, self.engine,
                  f"Challengers Defeated: {s.challengers_beaten}",
                  SCREEN_W - 40, 28, 22, C_GREEN, anchor="topright")

        # Matchup header
        draw_text(screen, self.engine, "TODAY'S MATCHUP",
                  SCREEN_W // 2, 90, 28, C_ACCENT, anchor="midtop", bold=True)

        # Defender panel (left)
        panel_w = SCREEN_W // 2 - 60
        def_panel = Panel(30, 130, panel_w, 710, title="DEFENDER",
                          border=(55, 145, 78), title_color=C_GREEN, shadow=True)
        def_panel.draw(screen, self.engine)

        member = s.league[s.challenger_position]
        draw_trainer_sprite(screen, self.engine, member.name, 50, 160, 144)
        draw_text(screen, self.engine, member.display_name(), 210, 172, 26,
                  C_TEXT_BRIGHT, bold=True)
        draw_text(screen, self.engine,
                  f"Stage {s.challenger_position + 1}/{len(s.league)}",
                  210, 205, 18, C_TEXT_DIM)
        if member.specialty:
            badge = TypeBadge(member.specialty, 210, 232, 14)
            badge.draw(screen, self.engine)

        dy = 315
        for p in member.team:
            h = draw_pokemon_card(screen, self.engine, p, 50, dy,
                                  panel_w - 50, show_moves=True)
            dy += h + 8

        # Challenger panel (right)
        challenger = s.current_challenger
        chall_x = SCREEN_W // 2 + 30
        chall_panel = Panel(chall_x, 130, panel_w, 710, title="CHALLENGER",
                            border=(185, 55, 55), title_color=C_RED, shadow=True)
        chall_panel.draw(screen, self.engine)

        draw_text(screen, self.engine, challenger.display_name(),
                  chall_x + 25, 170, 26, C_TEXT_BRIGHT, bold=True)

        cy = 210
        for p in challenger.team:
            h = draw_pokemon_card(screen, self.engine, p, chall_x + 20, cy,
                                  panel_w - 50, show_moves=True)
            cy += h + 8

        # VS divider
        vs_x = SCREEN_W // 2
        # Decorative line
        pygame.draw.line(screen, C_PANEL_BORDER, (vs_x, 150), (vs_x, 790), 2)
        # VS badge
        vs_panel = pygame.Rect(vs_x - 35, 395, 70, 50)
        pygame.draw.rect(screen, (50, 25, 25), vs_panel, border_radius=8)
        pygame.draw.rect(screen, C_GOLD, vs_panel, 2, border_radius=8)
        draw_text(screen, self.engine, "VS", vs_x, 405, 32, C_GOLD,
                  anchor="midtop", bold=True)

        # Buttons
        for btn in self.buttons:
            btn.draw(screen, self.engine)


# ─── Battle Scene ───────────────────────────────────────────────────

class BattleScene(Scene):
    """Interactive battle with B/W2 inspired graphical UI."""

    FIELD_H = 660  # Height of the battle field area

    def __init__(self, state, player_trainer, enemy_trainer):
        super().__init__()
        self.state = state
        self.player_trainer = player_trainer
        self.enemy_trainer = enemy_trainer
        self.player_poke = player_trainer.first_available()
        self.enemy_poke = enemy_trainer.first_available()
        self.phase = "choose_move"
        self.log = MessageLog(25, 685, 940, 370, font_size=18)
        self.move_buttons = []
        self.switch_buttons = []
        self.done_button = None
        self.anim_events = []
        self.anim_timer = 0
        self.anim_delay = 0.6
        self.result = None
        self.battle_state = BattleState()
        self._battle_bg = None
        self.player_poke.reset_battle_state()
        self.enemy_poke.reset_battle_state()
        self._build_move_buttons()
        self.log.add(f"{player_trainer.name} sends out {self.player_poke.species}!",
                     C_GREEN)
        self.log.add(f"{enemy_trainer.name} sends out {self.enemy_poke.species}!",
                     C_RED)
        for ev in do_switch_in_effects(self.player_poke, 0, self.battle_state):
            self._log_event(ev)
        for ev in do_switch_in_effects(self.enemy_poke, 1, self.battle_state):
            self._log_event(ev)
        if self.player_poke.ability == "Intimidate":
            actual = self.enemy_poke.change_stat("atk", -1)
            if actual:
                self.log.add(
                    f"{self.enemy_poke.species}'s Attack fell! (Intimidate)",
                    C_YELLOW)
        if self.enemy_poke.ability == "Intimidate":
            actual = self.player_poke.change_stat("atk", -1)
            if actual:
                self.log.add(
                    f"{self.player_poke.species}'s Attack fell! (Intimidate)",
                    C_YELLOW)

    def _create_battle_bg(self):
        """Pre-render the battle field background."""
        fh = self.FIELD_H
        surf = pygame.Surface((SCREEN_W, fh))
        sky_h = int(fh * 0.58)
        # Sky gradient
        for y in range(sky_h):
            t = y / max(sky_h - 1, 1)
            r = int(C_BATTLE_SKY_TOP[0] +
                    (C_BATTLE_SKY_BOT[0] - C_BATTLE_SKY_TOP[0]) * t)
            g = int(C_BATTLE_SKY_TOP[1] +
                    (C_BATTLE_SKY_BOT[1] - C_BATTLE_SKY_TOP[1]) * t)
            b = int(C_BATTLE_SKY_TOP[2] +
                    (C_BATTLE_SKY_BOT[2] - C_BATTLE_SKY_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W - 1, y))
        # Ground gradient
        for y in range(sky_h, fh):
            t = (y - sky_h) / max(fh - sky_h - 1, 1)
            r = int(C_BATTLE_GROUND[0] +
                    (C_BATTLE_GROUND_DARK[0] - C_BATTLE_GROUND[0]) * t)
            g = int(C_BATTLE_GROUND[1] +
                    (C_BATTLE_GROUND_DARK[1] - C_BATTLE_GROUND[1]) * t)
            b = int(C_BATTLE_GROUND[2] +
                    (C_BATTLE_GROUND_DARK[2] - C_BATTLE_GROUND[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_W - 1, y))
        # Battle platforms
        # Enemy platform (smaller, top-right)
        pygame.draw.ellipse(surf, C_BATTLE_PLATFORM_SHADOW,
                            (1260, 335, 280, 60))
        pygame.draw.ellipse(surf, C_BATTLE_PLATFORM,
                            (1265, 330, 270, 55))
        pygame.draw.ellipse(surf, (175, 145, 100),
                            (1275, 335, 250, 40), 2)
        # Player platform (larger, bottom-left)
        pygame.draw.ellipse(surf, C_BATTLE_PLATFORM_SHADOW,
                            (280, 550, 340, 72))
        pygame.draw.ellipse(surf, C_BATTLE_PLATFORM,
                            (285, 545, 330, 66))
        pygame.draw.ellipse(surf, (175, 145, 100),
                            (295, 550, 310, 50), 2)
        return surf

    def _build_move_buttons(self):
        self.move_buttons = []
        if not self.player_poke or self.player_poke.is_fainted():
            return
        for i, move_name in enumerate(self.player_poke.moves):
            md = MOVES_DB.get(move_name, {})
            mtype = md.get("type", "Normal")
            mcolor = type_color(mtype)
            raw_cat = md.get("category", "physical")
            cat = "PHY" if raw_cat == "physical" else (
                "STA" if raw_cat == "status" else "SPE")
            pw = md.get("power", 0)
            pw_str = str(pw) if pw else "—"
            label = f"{move_name}"

            col = i % 2
            row = i // 2
            bx = 990 + col * 460
            by = 685 + row * 192
            bw = 448
            bh = 184

            r, g, b = mcolor
            btn_color = (r // 4 + 18, g // 4 + 18, b // 4 + 18)
            btn_hover = (r // 3 + 25, g // 3 + 25, b // 3 + 25)

            btn = Button(label, bx, by, bw, bh,
                         callback=lambda m=move_name: self._select_move(m),
                         font_size=24, color=btn_color, hover_color=btn_hover,
                         border_color=mcolor, tag=move_name)
            self.move_buttons.append(btn)

    def _build_switch_buttons(self):
        self.switch_buttons = []
        available = [(i, p) for i, p in enumerate(self.player_trainer.team)
                     if not p.is_fainted()]
        for j, (idx, p) in enumerate(available):
            col = j % 2
            row = j // 2
            bx = 990 + col * 460
            by = 720 + row * 90
            label = f"{p.species} Lv.{p.level}  HP: {p.current_hp}/{p.max_hp}"
            btn = Button(label, bx, by, 448, 80,
                         callback=lambda poke=p: self._switch_to(poke),
                         font_size=18, color=(35, 55, 45), hover_color=(45, 75, 55),
                         border_color=C_GREEN, tag=p.species)
            self.switch_buttons.append(btn)

    def _log_event(self, ev):
        t = ev.get("type", "")
        if t == "weather":
            self.log.add(f"The weather changed to {ev['weather']}!", C_ACCENT)
        elif t == "ability_announce":
            self.log.add(f"{ev['pokemon']}'s {ev['ability']}!", C_YELLOW)
        elif t == "hazard_damage":
            self.log.add(
                f"{ev['target']} was hurt by {ev['hazard']}! ({ev['damage']} dmg)",
                C_RED)
        elif t == "status_inflict":
            self.log.add(
                f"{ev['target']} was afflicted with {ev['status']}!", C_YELLOW)
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
        first, second = determine_turn_order(
            self.player_poke, self.enemy_poke, move_name, enemy_move, bs)
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
        all_events = []
        for atk, dfn, move, side, atk_side in turns:
            if atk.is_fainted():
                break
            events = execute_move(atk, dfn, move, bs, atk_side)
            for ev in events:
                ev["side"] = side
            all_events.extend(events)
            if dfn.is_fainted():
                if side == "player":
                    next_poke = self.enemy_trainer.first_available()
                    if next_poke:
                        all_events.append({"type": "send_out", "side": "enemy",
                                           "trainer": self.enemy_trainer.name,
                                           "species": next_poke.species})
                    else:
                        all_events.append(
                            {"type": "battle_end", "winner": "player"})
                else:
                    next_poke = self.player_trainer.first_available()
                    if next_poke:
                        all_events.append(
                            {"type": "need_switch", "side": "player"})
                    else:
                        all_events.append(
                            {"type": "battle_end", "winner": "enemy"})
                break
            if atk.is_fainted():
                if side == "player":
                    next_poke = self.player_trainer.first_available()
                    if next_poke:
                        all_events.append(
                            {"type": "need_switch", "side": "player"})
                    else:
                        all_events.append(
                            {"type": "battle_end", "winner": "enemy"})
                else:
                    next_poke = self.enemy_trainer.first_available()
                    if next_poke:
                        all_events.append(
                            {"type": "send_out", "side": "enemy",
                             "trainer": self.enemy_trainer.name,
                             "species": next_poke.species})
                    else:
                        all_events.append(
                            {"type": "battle_end", "winner": "player"})
                break

        if (self.result is None and not self.player_poke.is_fainted()
                and not self.enemy_poke.is_fainted()):
            eot_events = do_turn_end_effects(
                self.player_poke, self.enemy_poke, bs)
            for ev in eot_events:
                if ev.get("target") == self.player_poke.species:
                    ev["side"] = "player"
                else:
                    ev["side"] = "enemy"
            all_events.extend(eot_events)
            for poke, side_name, trainer in [
                (self.player_poke, "player", self.player_trainer),
                (self.enemy_poke, "enemy", self.enemy_trainer),
            ]:
                if poke.is_fainted():
                    if side_name == "player":
                        next_p = trainer.first_available()
                        if next_p:
                            all_events.append(
                                {"type": "need_switch", "side": "player"})
                        else:
                            all_events.append(
                                {"type": "battle_end", "winner": "enemy"})
                    else:
                        next_p = trainer.first_available()
                        if next_p:
                            all_events.append(
                                {"type": "send_out", "side": "enemy",
                                 "trainer": self.enemy_trainer.name,
                                 "species": next_p.species})
                        else:
                            all_events.append(
                                {"type": "battle_end", "winner": "player"})

        self.anim_events = all_events
        self.anim_timer = 0

    def _switch_to(self, poke):
        self.player_poke = poke
        poke.reset_battle_state()
        self.log.add(f"Go, {poke.species}!", C_GREEN)
        sin_events = do_switch_in_effects(poke, 0, self.battle_state)
        for ev in sin_events:
            self._log_event(ev)
        if poke.ability == "Intimidate" and not self.enemy_poke.is_fainted():
            actual = self.enemy_poke.change_stat("atk", -1)
            if actual:
                self.log.add(
                    f"{self.enemy_poke.species}'s Attack fell! (Intimidate)",
                    C_YELLOW)
        if poke.is_fainted():
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
            self.log.add(
                f"{ev['target']} took {ev['damage']} damage! "
                f"({ev['hp']}/{ev['max_hp']} HP)", C_RED)
        elif t == "faint":
            self.log.add(f"{ev['target']} fainted!", C_RED)
            if ev.get("side") == "player":
                bounty = 10 + self.state.challengers_beaten * 2
                self.state.money += bounty
                self.log.add(f"+${bounty} for defeating {ev['target']}!", C_GOLD)
        elif t == "send_out":
            self.enemy_poke = self.enemy_trainer.first_available()
            if self.enemy_poke:
                self.enemy_poke.reset_battle_state()
                self.log.add(
                    f"{ev['trainer']} sends out {ev['species']}!", C_RED)
                sin = do_switch_in_effects(
                    self.enemy_poke, 1, self.battle_state)
                for sev in sin:
                    self._log_event(sev)
                if (self.enemy_poke.ability == "Intimidate"
                        and not self.player_poke.is_fainted()):
                    actual = self.player_poke.change_stat("atk", -1)
                    if actual:
                        self.log.add(
                            f"{self.player_poke.species}'s Attack fell! "
                            f"(Intimidate)", C_YELLOW)
        elif t == "need_switch":
            available = [(i, p)
                         for i, p in enumerate(self.player_trainer.team)
                         if not p.is_fainted()]
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
            self.log.add(
                f"{ev['user']} tried to use {ev['move']}, but it failed!",
                C_TEXT_DIM)
        elif t == "status_inflict":
            self.log.add(
                f"{ev['target']} was afflicted with {ev['status']}!", C_YELLOW)
        elif t == "status_cure":
            self.log.add(
                f"{ev['target']} was cured of {ev['status']}!", C_GREEN)
        elif t == "status_immobile":
            status_msgs = {
                "sleep": f"{ev['target']} is fast asleep!",
                "freeze": f"{ev['target']} is frozen solid!",
                "paralysis": f"{ev['target']} is paralyzed! It can't move!",
                "flinch": f"{ev['target']} flinched!",
                "infatuation": f"{ev['target']} is immobilized by love!",
            }
            self.log.add(
                status_msgs.get(ev["status"],
                                f"{ev['target']} can't move!"), C_YELLOW)
        elif t == "status_damage":
            self.log.add(
                f"{ev['target']} was hurt by {ev['status']}! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "confusion_hit":
            self.log.add(
                f"{ev['target']} hurt itself in confusion! "
                f"({ev['damage']} dmg)", C_YELLOW)
        elif t == "stat_change":
            direction = "rose" if ev["amount"] > 0 else "fell"
            sharply = "sharply " if abs(ev["amount"]) >= 2 else ""
            self.log.add(
                f"{ev['target']}'s {ev['stat']} {sharply}{direction}!",
                C_ACCENT)
        elif t == "recoil":
            self.log.add(
                f"{ev['target']} was hurt by recoil! ({ev['damage']} dmg)",
                C_RED)
        elif t == "drain":
            self.log.add(
                f"{ev['target']} restored {ev['amount']} HP!", C_GREEN)
        elif t == "heal":
            self.log.add(
                f"{ev['target']} restored HP! ({ev['hp']}/{ev['max_hp']})",
                C_GREEN)
        elif t == "protect":
            self.log.add(f"{ev['target']} protected itself!", C_GREEN)
        elif t == "protected":
            self.log.add(f"{ev['target']} protected itself!", C_GREEN)
        elif t == "substitute":
            self.log.add(f"{ev['target']} created a substitute!", C_ACCENT)
        elif t == "weather":
            self.log.add(
                f"The weather changed to {ev['weather']}!", C_ACCENT)
        elif t == "weather_end":
            self.log.add(f"The {ev['weather']} subsided!", C_TEXT_DIM)
        elif t == "weather_damage":
            self.log.add(
                f"{ev['target']} was buffeted by {ev['weather']}! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "hazard_set":
            self.log.add(f"{ev['hazard']} was set up!", C_ACCENT)
        elif t == "hazard_damage":
            self.log.add(
                f"{ev['target']} was hurt by {ev['hazard']}! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "hazard_clear":
            self.log.add("The hazards were cleared!", C_GREEN)
        elif t == "screen_set":
            self.log.add(f"{ev['screen']} was set up!", C_ACCENT)
        elif t == "screen_end":
            self.log.add(f"The {ev['screen']} wore off!", C_TEXT_DIM)
        elif t == "tailwind":
            self.log.add("Tailwind blew from behind!", C_ACCENT)
        elif t == "tailwind_end":
            self.log.add("The tailwind died down!", C_TEXT_DIM)
        elif t == "leech_seed":
            self.log.add(
                f"{ev['target']}'s health was sapped by Leech Seed! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "curse_damage":
            self.log.add(
                f"{ev['target']} was afflicted by the curse! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "curse_ghost":
            self.log.add(
                f"{ev['user']} cut its own HP to lay a curse on "
                f"{ev['target']}!", C_RED)
        elif t == "item_heal":
            self.log.add(
                f"{ev['target']} restored HP with {ev['item']}! "
                f"(+{ev['amount']})", C_GREEN)
        elif t == "item_damage":
            self.log.add(
                f"{ev['target']} was hurt by {ev['item']}! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "ability_heal":
            self.log.add(
                f"{ev['target']} healed with {ev['ability']}! "
                f"(+{ev['amount']})", C_GREEN)
        elif t == "ability_cure":
            self.log.add(
                f"{ev['target']}'s {ev['ability']} cured its "
                f"{ev['status']}!", C_GREEN)
        elif t == "ability_stat":
            self.log.add(
                f"{ev['target']}'s {ev['ability']} raised its "
                f"{ev['stat']}!", C_ACCENT)
        elif t == "ability_end":
            self.log.add(
                f"{ev['target']}'s {ev['ability']} wore off!", C_TEXT_DIM)
        elif t == "ability_immune":
            self.log.add(
                f"{ev['target']}'s {ev['ability']} nullified the attack!",
                C_GREEN)
        elif t == "ability_contact_damage":
            self.log.add(
                f"{ev['target']} was hurt by {ev['ability']}! "
                f"({ev['damage']} dmg)", C_RED)
        elif t == "ability_status":
            self.log.add(
                f"{ev['target']} was afflicted by {ev['ability']}! "
                f"({ev['status']})", C_YELLOW)
        elif t == "ability_announce":
            self.log.add(
                f"{ev['pokemon']}'s {ev['ability']}!", C_YELLOW)
        elif t == "field_set":
            self.log.add(
                f"{ev['effect']} twisted the dimensions!", C_ACCENT)
        elif t == "field_end":
            self.log.add(f"{ev['effect']} wore off!", C_TEXT_DIM)
        elif t == "haze":
            self.log.add("All stat changes were reset!", C_ACCENT)
        elif t == "belly_drum":
            self.log.add(
                f"{ev['target']} cut its HP and maxed its Attack!", C_GOLD)
        elif t == "nightmare_damage":
            self.log.add(
                f"{ev['target']} was hurt by Nightmare! "
                f"({ev['damage']} dmg)", C_RED)

    def _build_done_button(self):
        label = ("Victory! Continue..." if self.result
                 else "Defeat... Continue...")
        color = C_GREEN if self.result else C_RED
        self.done_button = Button(label, SCREEN_W // 2 - 150, 850, 300, 55,
                                  callback=self._finish, font_size=22,
                                  border_color=color)

    def _finish(self):
        s = self.state
        is_champion_fight = (self.player_trainer is s.champion)

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
        # ── Battle Background ──
        if self._battle_bg is None:
            self._battle_bg = self._create_battle_bg()
        screen.blit(self._battle_bg, (0, 0))

        # ── Action Panel Background ──
        action_rect = pygame.Rect(0, self.FIELD_H, SCREEN_W,
                                  SCREEN_H - self.FIELD_H)
        pygame.draw.rect(screen, C_ACTION_PANEL, action_rect)
        pygame.draw.line(screen, C_ACTION_BORDER,
                         (0, self.FIELD_H), (SCREEN_W, self.FIELD_H), 3)

        # ── Pokemon Sprites ──
        if self.player_poke and not self.player_poke.is_fainted():
            spr = self.engine.get_sprite(self.player_poke.species, 260)
            if spr:
                screen.blit(spr, (320, 290))
            else:
                draw_text(screen, self.engine, self.player_poke.species,
                          450, 420, 22, C_TEXT_DIM, anchor="center")
        if self.enemy_poke and not self.enemy_poke.is_fainted():
            spr = self.engine.get_sprite(self.enemy_poke.species, 220)
            if spr:
                screen.blit(spr, (1290, 100))
            else:
                draw_text(screen, self.engine, self.enemy_poke.species,
                          1400, 210, 22, C_TEXT_DIM, anchor="center")

        # ── Weather Indicator ──
        if self.battle_state.weather != Weather.NONE:
            weather_labels = {
                Weather.HARSH_SUNLIGHT: ("☀ Harsh Sunlight", C_YELLOW),
                Weather.RAIN: ("🌧 Rain", (100, 155, 255)),
                Weather.SANDSTORM: ("⛈ Sandstorm", (205, 185, 125)),
                Weather.HAILSTORM: ("❄ Hailstorm", (185, 225, 255)),
            }
            wl, wc = weather_labels.get(
                self.battle_state.weather, ("???", C_TEXT_DIM))
            wr = pygame.Rect(SCREEN_W // 2 - 110, 8, 220, 32)
            pygame.draw.rect(screen, (20, 25, 45), wr, border_radius=8)
            pygame.draw.rect(screen, wc, wr, 2, border_radius=8)
            draw_text(screen, self.engine, wl, SCREEN_W // 2, 14, 18, wc,
                      anchor="midtop", bold=True)

        # ── Enemy Info Box ──
        self._draw_info_box(screen, self.enemy_poke, self.enemy_trainer,
                            40, 35, 540, 145, is_player=False)

        # ── Player Info Box ──
        self._draw_info_box(screen, self.player_poke, self.player_trainer,
                            1330, 430, 560, 210, is_player=True)

        # ── VS Header ──
        draw_trainer_sprite(screen, self.engine, self.player_trainer.name,
                            15, self.FIELD_H + 8, 38)
        draw_text(screen, self.engine,
                  f"{self.player_trainer.display_name()}  vs  "
                  f"{self.enemy_trainer.display_name()}",
                  SCREEN_W // 2, self.FIELD_H + 14, 20, C_TEXT_DIM,
                  anchor="midtop")
        draw_trainer_sprite(screen, self.engine, self.enemy_trainer.name,
                            SCREEN_W - 53, self.FIELD_H + 8, 38)

        # ── Message Log ──
        self.log.draw(screen, self.engine)

        # ── Move/Switch/Done Buttons ──
        if self.phase == "choose_move":
            for btn in self.move_buttons:
                self._draw_move_button(screen, btn)
        elif self.phase == "switch":
            draw_text(screen, self.engine, "Choose your next Pokemon:",
                      1220, 695, 22, C_ACCENT, anchor="midtop", bold=True)
            for btn in self.switch_buttons:
                if btn.tag:
                    draw_pokemon_sprite(screen, self.engine, btn.tag,
                                        btn.rect.x + 10, btn.rect.y + 15, 48)
                btn.draw(screen, self.engine)
        elif self.phase == "done" and self.done_button:
            self.done_button.draw(screen, self.engine)
        elif self.phase == "animating":
            # Pulsing dots indicator
            anim_x = 1220
            anim_y = 860
            draw_text(screen, self.engine, "· · ·", anim_x, anim_y, 36,
                      C_TEXT_DIM, anchor="center")

    def _draw_info_box(self, screen, poke, trainer, x, y, w, h,
                       is_player=False):
        """Draw a B/W2-style Pokemon info box."""
        if not poke:
            return
        # Shadow
        sr = pygame.Rect(x + 4, y + 4, w, h)
        pygame.draw.rect(screen, (10, 14, 25), sr, border_radius=14)
        # Background
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (28, 35, 58), box, border_radius=14)
        # Colored top bar (green for player, red for enemy)
        bar_color = (45, 120, 65) if is_player else (140, 45, 45)
        bar = pygame.Rect(x + 3, y + 3, w - 6, 6)
        pygame.draw.rect(screen, bar_color, bar, border_radius=3)
        # Border
        border_c = (55, 135, 72) if is_player else (155, 52, 52)
        pygame.draw.rect(screen, border_c, box, 2, border_radius=14)

        # Name + Level
        nm_y = y + 18
        draw_text(screen, self.engine, poke.species, x + 18, nm_y, 26,
                  C_TEXT_BRIGHT, bold=True)
        lv_text = f"Lv.{poke.level}"
        draw_text(screen, self.engine, lv_text, x + w - 18, nm_y, 22,
                  C_TEXT_DIM, anchor="topright", bold=True)

        # Type badges
        draw_type_badges(screen, self.engine, poke.types, x + 18, nm_y + 32,
                         13)

        # HP bar
        hp_y = nm_y + 58
        hp_bar_w = w - 40
        hp_bar_h = 22 if is_player else 20
        hp = HPBar(x + 18, hp_y, hp_bar_w, hp_bar_h,
                   poke.current_hp, poke.max_hp,
                   show_numbers=is_player)
        hp.draw(screen, self.engine)

        # Status badge
        status_y = hp_y + hp_bar_h + 6
        if poke.status1 != Status1.NONE:
            draw_status_badge(screen, self.engine, poke.status1,
                              x + 18, status_y)

        if is_player:
            # Stats line
            stat_y = hp_y + hp_bar_h + 8
            stat_str = (f"ATK:{poke.atk}  DEF:{poke.defense}  "
                        f"SPA:{poke.spa}  SPD:{poke.spd}  SPE:{poke.spe}")
            draw_text(screen, self.engine, stat_str, x + 18, stat_y + 22,
                      14, C_TEXT_DIM)

        # Pokeball indicators
        ball_y = y + h - 28
        draw_pokeball_indicators(screen, trainer.team, x + 18, ball_y,
                                 size=16, gap=5)

    def _draw_move_button(self, screen, btn):
        """Draw a B/W2-style type-colored move button."""
        md = MOVES_DB.get(btn.tag, {})
        mtype = md.get("type", "Normal")
        mcolor = type_color(mtype)
        r, g, b = mcolor

        # Background
        bg = btn.hover_color if btn.hovered else btn.color
        # Shadow
        sr = btn.rect.move(3, 3)
        pygame.draw.rect(screen, (6, 8, 15), sr, border_radius=14)
        pygame.draw.rect(screen, bg, btn.rect, border_radius=14)

        # Type color stripe at top
        stripe = pygame.Rect(btn.rect.x + 4, btn.rect.y + 4,
                              btn.rect.w - 8, 7)
        pygame.draw.rect(screen, mcolor, stripe, border_radius=4)

        # Glow effect on hover
        if btn.hovered:
            glow = btn.rect.inflate(4, 4)
            pygame.draw.rect(screen, mcolor, glow, 3, border_radius=16)
        else:
            pygame.draw.rect(screen, btn.border_color, btn.rect, 2,
                             border_radius=14)

        # Move name (large, centered)
        name_font = self.engine.font_bold(26)
        name_surf = name_font.render(btn.tag, True, C_TEXT_BRIGHT)
        name_rect = name_surf.get_rect(
            midtop=(btn.rect.centerx, btn.rect.y + 22))
        screen.blit(name_surf, name_rect)

        # Type badge
        badge = TypeBadge(mtype, btn.rect.x + 16, btn.rect.bottom - 52, 15)
        badge.draw(screen, self.engine)

        # Category
        cat = md.get("category", "physical")
        cat_text = ("Physical" if cat == "physical"
                    else ("Status" if cat == "status" else "Special"))
        cat_color = ((240, 140, 60) if cat == "physical"
                     else ((150, 150, 180) if cat == "status"
                           else (120, 140, 250)))
        cat_font = self.engine.font(15)
        cat_surf = cat_font.render(cat_text, True, cat_color)
        screen.blit(cat_surf, (btn.rect.x + 16, btn.rect.bottom - 28))

        # Power
        pw = md.get("power", 0)
        pw_text = f"Power: {pw}" if pw else "Power: —"
        pw_font = self.engine.font_bold(16)
        pw_surf = pw_font.render(pw_text, True, C_TEXT)
        pw_rect = pw_surf.get_rect(
            bottomright=(btn.rect.right - 16, btn.rect.bottom - 14))
        screen.blit(pw_surf, pw_rect)

        # Accuracy
        acc = md.get("accuracy", 100)
        acc_text = f"Acc: {acc}%" if acc and acc < 101 else "Acc: —"
        acc_font = self.engine.font(14)
        acc_surf = acc_font.render(acc_text, True, C_TEXT_DIM)
        acc_rect = acc_surf.get_rect(
            bottomright=(btn.rect.right - 16, btn.rect.bottom - 34))
        screen.blit(acc_surf, acc_rect)


# ─── Result Scene (post-battle) ─────────────────────────────────────

class ResultScene(Scene):
    """Shows battle result and transitions to next day."""

    def __init__(self, state, won, reward):
        super().__init__()
        self.state = state
        self.won = won
        self.reward = reward
        self.btn = Button("Continue", SCREEN_W // 2 - 120, 650, 240, 55,
                          callback=self._continue, font_size=22,
                          border_color=C_GREEN if won else C_YELLOW)

    def _continue(self):
        from overworld import OverworldScene
        self.engine.set_scene(OverworldScene(self.state))

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)

    def draw(self, screen):
        screen.fill(C_BG)
        s = self.state

        # Decorative gradient
        gradient_color = (30, 50, 30) if self.won else (50, 30, 30)
        draw_gradient_v(screen, (0, 0, SCREEN_W, 350), gradient_color, C_BG)

        if self.won:
            draw_text(screen, self.engine, "VICTORY!",
                      SCREEN_W // 2, 200, 64, C_GOLD, anchor="center",
                      bold=True)
            draw_text(screen, self.engine, "The challenger has been defeated!",
                      SCREEN_W // 2, 310, 26, C_GREEN, anchor="center")
        else:
            draw_text(screen, self.engine, "DEFEAT",
                      SCREEN_W // 2, 200, 64, C_RED, anchor="center",
                      bold=True)
            draw_text(screen, self.engine, "The challenger advances!",
                      SCREEN_W // 2, 310, 26, C_YELLOW, anchor="center")
            remaining = len(s.league) - s.challenger_position
            if remaining <= 2:
                draw_text(screen, self.engine,
                          f"⚠ WARNING: {remaining} stage(s) from YOU!",
                          SCREEN_W // 2, 370, 24, C_RED, anchor="center",
                          bold=True)

        # Reward panel
        reward_panel = Panel(SCREEN_W // 2 - 160, 430, 320, 120,
                             shadow=True)
        reward_panel.draw(screen, self.engine)
        draw_text(screen, self.engine, f"+${self.reward}",
                  SCREEN_W // 2, 455, 42, C_YELLOW, anchor="midtop",
                  bold=True)
        draw_text(screen, self.engine, f"Total: ${s.money}",
                  SCREEN_W // 2, 510, 22, C_TEXT_DIM, anchor="midtop")

        self.btn.draw(screen, self.engine)


# ─── Shop Scene ─────────────────────────────────────────────────────

class ShopScene(Scene):
    """Shop for upgrades — tier-based system."""

    def __init__(self, state, target_member=None):
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
        self.scroll_y = 0
        if target_member is not None:
            self._pick_member(target_member)
        else:
            self._build_main()

    def _build_main(self):
        self.phase = "main"
        self.scroll_y = 0
        bx = SCREEN_W // 2 - 200
        self.buttons = [
            Button("Upgrade League Member", bx, 400, 400, 55,
                   callback=self._pick_member_start,
                   font_size=21, border_color=C_ACCENT),
            Button("View Teams", bx, 475, 400, 55,
                   callback=lambda: self._start_action("view_teams"),
                   font_size=21),
            Button("Back", bx, 560, 400, 55,
                   callback=self._back, font_size=21,
                   color=(55, 35, 35), hover_color=(75, 45, 45),
                   border_color=C_RED),
        ]
        self.sub_buttons = []

    def _start_action(self, action):
        if action == "view_teams":
            self.phase = "view_teams"
            self.scroll_y = 0
            self.sub_buttons = [
                Button("Back", SCREEN_W // 2 - 80, SCREEN_H - 70, 160, 48,
                       callback=self._build_main, font_size=18,
                       border_color=C_ACCENT),
            ]

    def _pick_member_start(self):
        self.phase = "pick_member"
        self.scroll_y = 0
        self.sub_buttons = []
        for i, member in enumerate(self.state.league):
            col = i % 2
            row = i // 2
            bx = 40 if col == 0 else 980
            by = 240 + row * 100
            label = f"{member.display_name()} ({len(member.team)} Pokemon)"
            btn = Button(label, bx, by, 900, 90,
                         callback=lambda m=member: self._pick_member(m),
                         font_size=22, border_color=C_ACCENT,
                         tag=member.name)
            self.sub_buttons.append(btn)
        total_rows = (len(self.state.league) + 1) // 2
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 100,
                   240 + total_rows * 100 + 15, 200, 50,
                   callback=self._build_main, font_size=18,
                   border_color=C_RED))

    def _pick_member(self, member):
        self.selected_member = member
        is_champion = (member is self.state.champion)
        if is_champion:
            self.phase = "champion_actions"
            self._build_champion_actions(member)
        else:
            self.phase = "member_actions"
            self._build_member_actions(member)

    def _build_champion_actions(self, member):
        self.scroll_y = 0
        self.sub_buttons = []
        for i, p in enumerate(member.team):
            col = i % 2
            row = i // 2
            bx = 40 if col == 0 else 980
            by = 280 + row * 110
            cost = 50
            label = f"Level Up {p.species} Lv.{p.level} → {p.level + 1}  (${cost})"
            btn = Button(label, bx, by, 900, 100,
                         callback=lambda poke=p: self._do_champion_levelup(poke),
                         font_size=22, border_color=C_GREEN, tag=p.species)
            self.sub_buttons.append(btn)
        total_rows = (len(member.team) + 1) // 2
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 100,
                   280 + total_rows * 110 + 15, 200, 50,
                   callback=self._build_main, font_size=18,
                   border_color=C_RED))

    def _do_champion_levelup(self, poke):
        if self.state.money < 50:
            self._show_message("Not enough money! Need $50.", C_RED)
            return
        poke.level_up(1)
        self.state.money -= 50
        self._show_message(
            f"{poke.species} leveled up to Lv.{poke.level}! (-$50)", C_GREEN)
        self._build_champion_actions(self.selected_member)

    def _build_member_actions(self, member):
        self.sub_buttons = []
        bx = SCREEN_W // 2 - 400
        next_species = member.get_next_tier_pokemon()
        if next_species:
            pdata = POKEMON_DB[next_species]
            types_str = "/".join(pdata["types"])
            pre_evo = EVOLVES_FROM.get(next_species)
            action_desc = (f"evolves {pre_evo}"
                           if pre_evo and any(
                               p.species == pre_evo for p in member.team)
                           else "adds to team")
            label = (f"Upgrade Pokemon: {next_species} [{types_str}] "
                     f"({action_desc})  ($200)")
            self.sub_buttons.append(
                Button(label, bx, 300, 800, 80,
                       callback=lambda: self._do_upgrade_pokemon(
                           member, next_species),
                       font_size=22, border_color=C_ACCENT,
                       tag=next_species))
        else:
            self.sub_buttons.append(
                Button("Pokemon: MAX TIER", bx, 300, 800, 80,
                       font_size=22, border_color=C_TEXT_DIM,
                       color=(40, 40, 45), hover_color=(40, 40, 45)))

        self.sub_buttons.append(
            Button("Upgrade Move  ($100)", bx, 400, 800, 80,
                   callback=lambda: self._pick_poke_for_move(member),
                   font_size=22, border_color=C_ACCENT))
        self.sub_buttons.append(
            Button("Level Up Team (+5 Lvls)  ($100)", bx, 500, 800, 80,
                   callback=lambda: self._do_team_levelup(member),
                   font_size=22, border_color=C_GREEN))
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 100, 605, 200, 50,
                   callback=self._build_main, font_size=18,
                   border_color=C_RED))

    def _do_upgrade_pokemon(self, member, species):
        if self.state.money < 200:
            self._show_message("Not enough money! Need $200.", C_RED)
            return
        avg_level = (sum(p.level for p in member.team) // len(member.team)
                     if member.team else 10)
        new_level = max(5, avg_level)
        member.add_tier_pokemon(species, new_level)
        self.state.money -= 200
        self._show_message(
            f"{species} Lv.{new_level} joined "
            f"{member.display_name()}'s team! (-$200)", C_GREEN)
        self._build_member_actions(member)

    def _do_team_levelup(self, member):
        if self.state.money < 100:
            self._show_message("Not enough money! Need $100.", C_RED)
            return
        for p in member.team:
            p.level_up(5)
        self.state.money -= 100
        self._show_message(
            f"All of {member.display_name()}'s Pokemon gained 5 levels! (-$100)",
            C_GREEN)
        self._build_member_actions(member)

    def _pick_poke_for_move(self, member):
        if self.state.money < 100:
            self._show_message("Not enough money! Need $100.", C_RED)
            return
        self.phase = "pick_poke_move"
        self.scroll_y = 0
        self.sub_buttons = []
        for i, p in enumerate(member.team):
            col = i % 2
            row = i // 2
            bx = 40 if col == 0 else 980
            by = 280 + row * 110
            label = f"{p.species} Lv.{p.level}  ({', '.join(p.moves)})"
            btn = Button(label, bx, by, 900, 100,
                         callback=lambda poke=p: self._show_move_upgrades(poke),
                         font_size=22, border_color=C_ACCENT, tag=p.species)
            self.sub_buttons.append(btn)
        total_rows = (len(member.team) + 1) // 2
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 100,
                   280 + total_rows * 110 + 15, 200, 50,
                   callback=lambda: self._build_member_actions(member),
                   font_size=18, border_color=C_RED))

    def _show_move_upgrades(self, poke):
        self.selected_poke = poke
        self.phase = "pick_move_upgrade"
        self.scroll_y = 0
        self.sub_buttons = []
        idx = 0

        for mtype, cur_tier, max_tier in poke.get_available_move_upgrades():
            tier_list = poke.move_tiers[mtype]
            cur_move = tier_list[cur_tier - 1]
            next_move = tier_list[cur_tier]
            label = f"{mtype}: {cur_move} → {next_move}  ($100)"
            mcolor = type_color(mtype)
            r, g, b = mcolor
            col = idx % 2
            row = idx // 2
            bx = 40 if col == 0 else 980
            by = 280 + row * 100
            btn = Button(label, bx, by, 900, 90,
                         callback=lambda mt=mtype: self._do_move_upgrade(
                             poke, mt),
                         font_size=22,
                         color=(r // 5 + 18, g // 5 + 18, b // 5 + 18),
                         hover_color=(r // 4 + 28, g // 4 + 28, b // 4 + 28),
                         border_color=mcolor)
            self.sub_buttons.append(btn)
            idx += 1

        for mtype in poke.get_learnable_new_types():
            tier_list = poke.move_tiers[mtype]
            first_move = tier_list[0]
            label = f"Learn {mtype}: {first_move}  ($100)"
            mcolor = type_color(mtype)
            r, g, b = mcolor
            col = idx % 2
            row = idx // 2
            bx = 40 if col == 0 else 980
            by = 280 + row * 100
            btn = Button(label, bx, by, 900, 90,
                         callback=lambda mt=mtype: self._do_move_upgrade(
                             poke, mt),
                         font_size=22,
                         color=(r // 5 + 18, g // 5 + 18, b // 5 + 18),
                         hover_color=(r // 4 + 28, g // 4 + 28, b // 4 + 28),
                         border_color=mcolor)
            self.sub_buttons.append(btn)
            idx += 1

        if idx == 0:
            self._show_message(f"{poke.species} has all moves maxed!",
                               C_YELLOW)
            self._build_member_actions(self.selected_member)
            return

        total_rows = (idx + 1) // 2
        self.sub_buttons.append(
            Button("Cancel", SCREEN_W // 2 - 100,
                   280 + total_rows * 100 + 15, 200, 50,
                   callback=lambda: self._build_member_actions(
                       self.selected_member),
                   font_size=18, border_color=C_RED))

    def _do_move_upgrade(self, poke, move_type):
        if self.state.money < 100:
            self._show_message("Not enough money! Need $100.", C_RED)
            return
        new_move = poke.upgrade_move_type(move_type)
        if new_move:
            self.state.money -= 100
            self._show_message(
                f"{poke.species} learned {new_move}! (-$100)", C_GREEN)
        self._build_member_actions(self.selected_member)

    def _show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 3.0

    def _back(self):
        from overworld import OverworldScene
        self.engine.set_scene(OverworldScene(self.state))

    def handle_events(self, events):
        for e in events:
            if self.phase == "main":
                for btn in self.buttons:
                    btn.handle_event(e)
            else:
                if e.type == pygame.MOUSEWHEEL:
                    old = self.scroll_y
                    self.scroll_y -= e.y * 35
                    self.scroll_y = max(0, self.scroll_y)
                    shift = old - self.scroll_y
                    for btn in self.sub_buttons:
                        btn.rect.y += shift
                for btn in self.sub_buttons:
                    btn.handle_event(e)

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, screen):
        screen.fill(C_BG)

        # Header gradient
        draw_gradient_v(screen, (0, 0, SCREEN_W, 100), (30, 40, 68), C_BG)

        draw_text(screen, self.engine, "POKEMON LEAGUE SHOP",
                  SCREEN_W // 2, 30, 40, C_GOLD, anchor="midtop", bold=True)

        # Money display with panel
        money_panel = Panel(SCREEN_W // 2 - 100, 80, 200, 42, shadow=True)
        money_panel.draw(screen, self.engine)
        draw_text(screen, self.engine, f"${self.state.money}",
                  SCREEN_W // 2, 88, 26, C_YELLOW, anchor="midtop",
                  bold=True)

        if self.message:
            msg_panel = Panel(SCREEN_W // 2 - 320, 135, 640, 40, shadow=True,
                              border=self.message_color)
            msg_panel.draw(screen, self.engine)
            draw_text(screen, self.engine, self.message,
                      SCREEN_W // 2, 145, 19, self.message_color,
                      anchor="midtop")

        if self.phase == "main":
            for btn in self.buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "view_teams":
            y = 190 - self.scroll_y
            for member in self.state.league:
                # Member header
                draw_trainer_sprite(screen, self.engine, member.name,
                                    60, y - 5, 60)
                draw_text(screen, self.engine, member.display_name(),
                          130, y, 24, C_ACCENT, bold=True)
                if member.specialty:
                    badge = TypeBadge(member.specialty, 420, y + 4, 14)
                    badge.draw(screen, self.engine)
                y += 65
                for p in member.team:
                    draw_pokemon_sprite(screen, self.engine, p.species,
                                        80, y - 5, 48)
                    types_str = "/".join(p.types)
                    moves_str = ", ".join(p.moves)
                    draw_text(screen, self.engine,
                              f"{p.species} Lv.{p.level} [{types_str}]",
                              140, y, 20, C_TEXT_BRIGHT)
                    draw_text(screen, self.engine, moves_str,
                              500, y + 3, 17, C_TEXT_DIM)
                    y += 50
                y += 18
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)

        elif self.phase == "champion_actions":
            draw_trainer_sprite(screen, self.engine,
                                self.selected_member.name,
                                SCREEN_W // 2 - 240, 190, 80)
            draw_text(screen, self.engine,
                      f"{self.selected_member.display_name()} "
                      f"— Level Up (+1 Lv, $50 each)",
                      SCREEN_W // 2 + 30, 215, 24, C_ACCENT, anchor="midtop",
                      bold=True)
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)
                if btn.tag:
                    draw_pokemon_sprite(screen, self.engine, btn.tag,
                                        btn.rect.x + 10, btn.rect.y + 10, 80)

        elif self.phase == "member_actions":
            draw_trainer_sprite(screen, self.engine,
                                self.selected_member.name,
                                SCREEN_W // 2 - 240, 190, 80)
            draw_text(screen, self.engine,
                      f"Upgrades for {self.selected_member.display_name()}:",
                      SCREEN_W // 2 + 30, 215, 24, C_ACCENT, anchor="midtop",
                      bold=True)
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)
                if btn.tag:
                    draw_pokemon_sprite(screen, self.engine, btn.tag,
                                        btn.rect.x + 10, btn.rect.y + 5, 70)

        elif self.phase in ("pick_poke_move", "pick_move_upgrade"):
            header = (f"Upgrade move for "
                      f"{self.selected_member.display_name()}:")
            if self.phase == "pick_move_upgrade":
                header = (f"Pick upgrade for "
                          f"{self.selected_poke.species}:  ($100)")
                draw_pokemon_sprite(screen, self.engine,
                                    self.selected_poke.species,
                                    SCREEN_W // 2 - 45, 180, 80)
            draw_text(screen, self.engine, header,
                      SCREEN_W // 2 + 30, 215, 24, C_ACCENT, anchor="midtop",
                      bold=True)
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)
                if btn.tag:
                    draw_pokemon_sprite(screen, self.engine, btn.tag,
                                        btn.rect.x + 10, btn.rect.y + 10, 80)

        else:
            if self.phase == "pick_member":
                draw_text(screen, self.engine, "Choose a League member:",
                          SCREEN_W // 2, 195, 28, C_ACCENT, anchor="midtop",
                          bold=True)
            for btn in self.sub_buttons:
                btn.draw(screen, self.engine)
                if self.phase == "pick_member" and btn.tag:
                    draw_trainer_sprite(screen, self.engine, btn.tag,
                                        btn.rect.x + 10, btn.rect.y + 10, 70)


# ─── League Overview Scene ──────────────────────────────────────────

class LeagueScene(Scene):
    """Display the full league in a graphical overview."""

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.scroll_y = 0
        self.btn = Button("Back", SCREEN_W // 2 - 80, SCREEN_H - 65, 160, 48,
                          callback=self._back, font_size=18,
                          border_color=C_ACCENT)

    def _back(self):
        from overworld import OverworldScene
        self.engine.set_scene(OverworldScene(self.state))

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)
            if e.type == pygame.MOUSEWHEEL:
                self.scroll_y -= e.y * 35
                self.scroll_y = max(0, self.scroll_y)

    def draw(self, screen):
        screen.fill(C_BG)
        # Header gradient
        draw_gradient_v(screen, (0, 0, SCREEN_W, 60), (30, 40, 68), C_BG)
        draw_text(screen, self.engine, "LEAGUE OVERVIEW",
                  SCREEN_W // 2, 15, 34, C_GOLD, anchor="midtop", bold=True)

        y = 75 - self.scroll_y
        for i, member in enumerate(self.state.league):
            is_challenger = (i == self.state.challenger_position and
                             self.state.current_challenger is not None)
            border = C_RED if is_challenger else C_PANEL_BORDER
            panel_h = 42 + len(member.team) * 34
            panel = Panel(50, y, SCREEN_W - 100, panel_h, border=border,
                          shadow=True)
            panel.draw(screen, self.engine)

            marker = "  ◄◄ CHALLENGER" if is_challenger else ""
            color = C_RED if is_challenger else C_ACCENT

            # Trainer sprite + name
            draw_trainer_sprite(screen, self.engine, member.name,
                                72, y + 8, 30)
            draw_text(screen, self.engine,
                      f"Stage {i + 1}: {member.display_name()}{marker}",
                      110, y + 10, 22, color, bold=True)

            # Specialty badge
            if member.specialty:
                badge = TypeBadge(member.specialty,
                                  SCREEN_W - 200, y + 10, 13)
                badge.draw(screen, self.engine)

            for j, p in enumerate(member.team):
                py = y + 42 + j * 34
                draw_pokemon_sprite(screen, self.engine, p.species,
                                    95, py, 26)
                draw_text(screen, self.engine, f"{p.species} Lv.{p.level}",
                          130, py + 2, 18, C_TEXT_BRIGHT)
                draw_type_badges(screen, self.engine, p.types, 330, py + 2,
                                 13)
                moves = ", ".join(p.moves)
                draw_text(screen, self.engine, moves, 560, py + 4, 15,
                          C_TEXT_DIM)

            y += panel_h + 10

        self.btn.draw(screen, self.engine)


# ─── Game Over Scene ────────────────────────────────────────────────

class GameOverScene(Scene):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.btn = Button("Exit Game", SCREEN_W // 2 - 120, 680, 240, 55,
                          callback=self._quit, font_size=22,
                          border_color=C_RED)

    def _quit(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, events):
        for e in events:
            self.btn.handle_event(e)

    def draw(self, screen):
        screen.fill((12, 8, 8))
        # Dramatic red gradient
        draw_gradient_v(screen, (0, 0, SCREEN_W, 400), (40, 10, 10),
                        (12, 8, 8))

        draw_text(screen, self.engine, "GAME OVER",
                  SCREEN_W // 2, 240, 72, C_RED, anchor="center", bold=True)

        # Decorative line
        pygame.draw.line(screen, (120, 30, 30),
                         (SCREEN_W // 2 - 200, 310),
                         (SCREEN_W // 2 + 200, 310), 2)

        draw_text(screen, self.engine, "The Champion has fallen!",
                  SCREEN_W // 2, 350, 28, C_TEXT_DIM, anchor="center")

        # Stats panel
        stats_panel = Panel(SCREEN_W // 2 - 200, 420, 400, 180, shadow=True,
                            border=C_RED)
        stats_panel.draw(screen, self.engine)
        draw_text(screen, self.engine, f"You lasted {self.state.day} days",
                  SCREEN_W // 2, 450, 26, C_TEXT, anchor="center")
        draw_text(screen, self.engine,
                  f"Challengers defeated: {self.state.challengers_beaten}",
                  SCREEN_W // 2, 500, 26, C_GOLD, anchor="center",
                  bold=True)
        draw_text(screen, self.engine, f"Final balance: ${self.state.money}",
                  SCREEN_W // 2, 545, 20, C_YELLOW, anchor="center")

        self.btn.draw(screen, self.engine)
