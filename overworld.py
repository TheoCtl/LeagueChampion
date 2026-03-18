"""
Pokemon League Champion - Overworld Scene
Fixed-camera 2D rooms with room transitions, gym interactions,
roaming Pokemon, and a choice menu for talking to gym leaders.
"""
import pygame
import sys
from engine import (
    Scene, SCREEN_W, SCREEN_H,
    C_BG, C_TEXT, C_TEXT_DIM, C_TEXT_BRIGHT, C_GOLD, C_YELLOW, C_GREEN,
    C_RED, C_ACCENT, C_PANEL, C_PANEL_BORDER, C_CYAN,
    draw_text, draw_gradient_v, TYPE_COLORS,
)
from world import (
    TILE_SIZE, MAP_W, MAP_H, MAP_OFFSET_Y,
    Player, RoamingPokemon, build_champion_room, build_gym,
)


class OverworldScene(Scene):
    """Fixed-camera room-based scene with gym navigation."""

    def __init__(self, state, target_room=None):
        super().__init__()
        self.state = state

        # Current room ID (e.g. "champion_room", "gym:Lenora", ...)
        self.current_room = target_room or getattr(
            state, 'current_room', 'champion_room')
        state.current_room = self.current_room

        # Build room
        self.game_map = self._build_room(self.current_room)

        # Player position
        px, py, pd = self._get_player_start()
        self.player = Player(px, py)
        self.player.direction = pd

        # Interaction state
        self.show_prompt = False
        self.prompt_text = ""
        self.prompt_action = None

        # Dialogue state
        self.dialogue_active = False
        self.dialogue_name = ""
        self.dialogue_text = ""

        # Choice menu state (for gym leader: Upgrade / Fight / Cancel)
        self.choice_active = False
        self.choice_options = []
        self.choice_selected = 0
        self.choice_npc = None

        # Fade transition
        self.fade_alpha = 255
        self.fading_in = True
        self.fading_out = False
        self.fade_target = None
        self.fade_callback = None
        self.fade_speed = 600

        # Door label tooltip
        self.door_label_timer = 0.0
        self.door_label_text = ""
        self.door_label_pos = (0, 0)

    def _build_room(self, room_id):
        """Build or rebuild the current room's GameMap."""
        if room_id == 'champion_room':
            cp = getattr(self.state, 'challenger_position', 0)
            return build_champion_room(self.state.league, cp)
        elif room_id.startswith('gym:'):
            leader_name = room_id[4:]
            for i, member in enumerate(self.state.league):
                if member.name == leader_name:
                    cp = getattr(self.state, 'challenger_position', 0)
                    return build_gym(member, i, cp)
        # Fallback
        return build_champion_room(self.state.league, 0)

    def _get_player_start(self):
        """Determine where the player spawns in the current room."""
        saved_room = getattr(self.state, '_saved_room', None)
        if saved_room == self.current_room:
            # Restore saved position within same room
            px = getattr(self.state, 'player_pos_x', MAP_W // 2)
            py = getattr(self.state, 'player_pos_y', MAP_H - 3)
            pd = getattr(self.state, 'player_dir', 'up')
            return px, py, pd

        if self.current_room == 'champion_room':
            # Entering hub — spawn at center bottom
            return MAP_W // 2, MAP_H - 3, 'up'
        else:
            # Entering a gym — spawn at exit door (bottom center), face up
            return 19, MAP_H - 3, 'up'

    def _save_player_pos(self):
        self.state.player_pos_x = self.player.grid_x
        self.state.player_pos_y = self.player.grid_y
        self.state.player_dir = self.player.direction
        self.state._saved_room = self.current_room

    # ── Events ─────────────────────────────────────────────────────

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if self.fading_out:
                    continue
                if self.choice_active:
                    self._handle_choice_key(e.key)
                    continue
                if self.dialogue_active:
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN,
                                 pygame.K_ESCAPE):
                        self.dialogue_active = False
                    continue
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._interact()
                elif e.key == pygame.K_ESCAPE:
                    self._try_quit()

    def _try_quit(self):
        pygame.quit()
        sys.exit()

    def _handle_choice_key(self, key):
        if key == pygame.K_UP:
            self.choice_selected = (
                (self.choice_selected - 1) % len(self.choice_options))
        elif key == pygame.K_DOWN:
            self.choice_selected = (
                (self.choice_selected + 1) % len(self.choice_options))
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            self._select_choice()
        elif key == pygame.K_ESCAPE:
            self.choice_active = False

    def _select_choice(self):
        choice = self.choice_options[self.choice_selected]
        self.choice_active = False
        if choice == 'upgrade':
            self._go_shop_for(self.choice_npc)
        elif choice == 'fight':
            self._go_fight()
        elif choice == 'league':
            self._go_league()

    # ── Interaction ────────────────────────────────────────────────

    def _interact(self):
        if not self.prompt_action:
            return
        if self.prompt_action.startswith('npc:'):
            name = self.prompt_action[4:]
            npc = self.game_map.get_npc_by_name(name)
            if npc and npc.role == 'gym_leader':
                self._open_leader_menu(npc)
            elif npc:
                self._talk_npc(npc)

    def _talk_npc(self, npc):
        self.dialogue_active = True
        self.dialogue_name = npc.name
        self.dialogue_text = npc.dialogue

    def _open_leader_menu(self, npc):
        """Show choice menu for gym leader (Upgrade / Fight / Cancel)."""
        leader_name = npc.name
        self.choice_npc = leader_name
        self.choice_options = ['upgrade']

        # Can we fight here? Only if this gym has the current challenger
        league_idx = None
        for i, m in enumerate(self.state.league):
            if m.name == leader_name:
                league_idx = i
                break
        cp = getattr(self.state, 'challenger_position', 0)
        if league_idx is not None and league_idx == cp:
            self.choice_options.insert(0, 'fight')

        self.choice_options.append('league')
        self.choice_options.append('cancel')
        self.choice_selected = 0
        self.choice_active = True

    def _go_shop_for(self, leader_name):
        """Open ShopScene pre-selected for this leader's member."""
        self._save_player_pos()
        from game import ShopScene
        # Find the member
        target = None
        for m in self.state.league:
            if m.name == leader_name:
                target = m
                break
        self._start_fade(ShopScene(self.state, target_member=target))

    def _go_fight(self):
        """Launch battle at the current challenger position."""
        self._save_player_pos()
        from game import DayScene
        # Ensure challenger
        if self.state.current_challenger is None:
            from generator import generate_challenger
            from pokemon import Trainer
            data = generate_challenger(self.state.challengers_beaten)
            self.state.current_challenger = Trainer(
                data["name"], data["title"], data["team"])
            self.state.challenger_position = (
                getattr(self.state, 'challenger_position', 0))
        self._start_fade(DayScene(self.state))

    def _go_league(self):
        self._save_player_pos()
        from game import LeagueScene
        self._start_fade(LeagueScene(self.state))

    def _enter_door(self, target):
        """Transition to another room via fade."""
        self._save_player_pos()
        self.state.current_room = target if target.startswith('gym:') \
            else target
        # Use a callback for room transition so we rebuild in-place
        self.fading_out = True
        self.fade_alpha = 0
        self.fade_target = None

        def _after_fade():
            if target == 'champion_room':
                new_room = 'champion_room'
            else:
                new_room = f"gym:{target}" if not target.startswith('gym:') \
                    else target
            self.engine.set_scene(OverworldScene(self.state, new_room))

        self.fade_callback = _after_fade

    def _start_fade(self, target_scene):
        self.fading_out = True
        self.fade_alpha = 0
        self.fade_target = target_scene
        self.fade_callback = None

    # ── Update ─────────────────────────────────────────────────────

    def update(self, dt):
        # Fade transitions
        if self.fading_in:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_in = False
            return
        if self.fading_out:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                if self.fade_target:
                    self.engine.set_scene(self.fade_target)
                elif self.fade_callback:
                    self.fade_callback()
            return

        if self.dialogue_active or self.choice_active:
            return

        # Movement
        keys = pygame.key.get_pressed()
        if not self.player.moving:
            moved = False
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                moved = self.player.try_move('up', self.game_map)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                moved = self.player.try_move('down', self.game_map)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moved = self.player.try_move('left', self.game_map)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moved = self.player.try_move('right', self.game_map)
            if not moved:
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.player.direction = 'up'
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.player.direction = 'down'
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.player.direction = 'left'
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.player.direction = 'right'

        self.player.update(dt)

        # Roaming Pokemon
        occupied = set()
        occupied.add((self.player.grid_x, self.player.grid_y))
        for npc in self.game_map.npcs:
            occupied.add((npc.grid_x, npc.grid_y))
        for rp in self.game_map.roaming:
            occupied.add((rp.grid_x, rp.grid_y))
        for rp in self.game_map.roaming:
            rp.update(dt, self.game_map, occupied)

        # Check door trigger (when player finishes moving onto a door)
        if not self.player.moving:
            self._check_door()

        # Check interaction prompts
        self._update_prompts()

    def _check_door(self):
        """If player is standing on a door tile, trigger transition."""
        px, py = self.player.grid_x, self.player.grid_y
        door_target = self.game_map.doors.get((px, py))
        if door_target and not self.fading_out:
            if self.current_room == 'champion_room':
                # Door target is a member name → go to their gym
                self._enter_door(f"gym:{door_target}")
            else:
                # Door target is "champion_room"
                self._enter_door(door_target)

    def _update_prompts(self):
        fx, fy = self.player.facing_tile()
        px, py = self.player.grid_x, self.player.grid_y

        standing = self.game_map.get_interaction(px, py)
        facing = self.game_map.get_interaction(fx, fy)
        interaction = facing or standing

        if interaction:
            if interaction.startswith('door:'):
                # Show door label briefly (but don't show prompt — auto-enter)
                self.show_prompt = False
                self.prompt_action = None
                return
            if interaction.startswith('npc:'):
                npc_name = interaction[4:]
                self.show_prompt = True
                self.prompt_text = f"Talk to {npc_name}"
                self.prompt_action = interaction
                return
        self.show_prompt = False
        self.prompt_action = None

    # ── Draw ───────────────────────────────────────────────────────

    def draw(self, screen):
        screen.fill((0, 0, 0))

        ox = 0
        oy = MAP_OFFSET_Y

        # Draw map
        map_surf = self.game_map.render()
        screen.blit(map_surf, (ox, oy))

        # Draw door labels (type name) above each door
        if self.current_room == 'champion_room':
            self._draw_door_labels(screen, ox, oy)

        # Draw roaming Pokemon
        for rp in self.game_map.roaming:
            spr = rp.get_sprite(self.engine)
            if spr:
                sw, sh = spr.get_size()
                rx = int(rp.pixel_x) + ox + (TILE_SIZE - sw) // 2
                ry = int(rp.pixel_y) + oy + (TILE_SIZE - sh) // 2
                screen.blit(spr, (rx, ry))

        # Draw NPCs
        for npc in self.game_map.npcs:
            sx = npc.grid_x * TILE_SIZE + ox
            sy = npc.grid_y * TILE_SIZE + oy
            spr = npc.get_sprite(self.engine)
            if spr:
                sw, sh = spr.get_size()
                screen.blit(spr, (sx + (TILE_SIZE - sw) // 2,
                                  sy + (TILE_SIZE - sh) // 2))
            draw_text(screen, self.engine, npc.name,
                      sx + TILE_SIZE // 2, sy - 6, 11,
                      C_TEXT_DIM, anchor="midbottom")

        # Draw player
        player_spr = self.player.get_sprite()
        if player_spr:
            ppx = int(self.player.pixel_x) + ox
            ppy = int(self.player.pixel_y) + oy
            screen.blit(player_spr, (ppx, ppy))

        # ── HUD ──
        self._draw_hud(screen)

        # ── Interaction prompt ──
        if self.show_prompt and not self.dialogue_active and \
                not self.choice_active:
            self._draw_prompt(screen)

        # ── Dialogue box ──
        if self.dialogue_active:
            self._draw_dialogue(screen)

        # ── Choice menu ──
        if self.choice_active:
            self._draw_choice(screen)

        # ── Location label ──
        self._draw_location(screen)

        # ── Fade overlay ──
        if self.fade_alpha > 0:
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            screen.blit(fade, (0, 0))

    # ── Door labels in champion room ───────────────────────────────

    def _draw_door_labels(self, screen, ox, oy):
        for (dx, dy), member in self.game_map._door_labels.items():
            tx = dx * TILE_SIZE + ox + TILE_SIZE // 2
            ty = dy * TILE_SIZE + oy - 4
            specialty = member.specialty or "Normal"
            color = TYPE_COLORS.get(specialty, C_TEXT_DIM)

            # Check if this is the challenger gym
            cp = getattr(self.state, 'challenger_position', 0)
            league_idx = None
            for i, m in enumerate(self.state.league):
                if m.name == member.name:
                    league_idx = i
                    break
            is_current = (league_idx == cp)

            draw_text(screen, self.engine, member.name,
                      tx, ty, 10, color, anchor="midbottom", bold=is_current)
            if is_current:
                # Draw a small star/arrow indicator
                draw_text(screen, self.engine, "!",
                          tx, ty - 11, 12, C_YELLOW,
                          anchor="midbottom", bold=True)

    # ── HUD ────────────────────────────────────────────────────────

    def _draw_hud(self, screen):
        hud = pygame.Surface((SCREEN_W, 44), pygame.SRCALPHA)
        hud.fill((18, 22, 38, 180))
        screen.blit(hud, (0, 0))
        pygame.draw.line(screen, (55, 65, 100), (0, 44), (SCREEN_W, 44), 1)

        draw_text(screen, self.engine, f"Day {self.state.day}",
                  20, 10, 22, C_GOLD, bold=True)
        draw_text(screen, self.engine, f"${self.state.money}",
                  160, 12, 20, C_YELLOW, bold=True)
        draw_text(screen, self.engine,
                  f"Challengers Defeated: {self.state.challengers_beaten}",
                  SCREEN_W - 20, 12, 18, C_GREEN, anchor="topright")

        # Controls hint
        hint = pygame.Surface((320, 30), pygame.SRCALPHA)
        hint.fill((18, 22, 38, 140))
        screen.blit(hint, (0, SCREEN_H - 30))
        draw_text(screen, self.engine,
                  "ARROWS: Move  |  SPACE: Interact",
                  10, SCREEN_H - 26, 13, C_TEXT_DIM)

    # ── Interaction prompt ─────────────────────────────────────────

    def _draw_prompt(self, screen):
        text = f"[SPACE]  {self.prompt_text}"
        font = self.engine.font(18)
        tw, th = font.size(text)
        bw = tw + 40
        bh = 42
        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H - 90

        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((18, 22, 38, 210))
        screen.blit(bg, (bx, by))
        pygame.draw.rect(screen, C_ACCENT, (bx, by, bw, bh), 2,
                         border_radius=6)
        draw_text(screen, self.engine, text,
                  SCREEN_W // 2, by + 10, 18, C_TEXT_BRIGHT, anchor="midtop")

    # ── Dialogue box ───────────────────────────────────────────────

    def _draw_dialogue(self, screen):
        box_w = 800
        box_h = 160
        bx = SCREEN_W // 2 - box_w // 2
        by = SCREEN_H - box_h - 40

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((18, 22, 38, 230))
        screen.blit(bg, (bx, by))
        pygame.draw.rect(screen, C_PANEL_BORDER, (bx, by, box_w, box_h), 2,
                         border_radius=8)

        pygame.draw.rect(screen, (28, 34, 58),
                         (bx + 10, by - 18, 160, 24), border_radius=4)
        pygame.draw.rect(screen, C_ACCENT,
                         (bx + 10, by - 18, 160, 24), 1, border_radius=4)
        draw_text(screen, self.engine, self.dialogue_name,
                  bx + 20, by - 16, 16, C_ACCENT, bold=True)

        lines = self.dialogue_text.split('\n')
        for i, line in enumerate(lines):
            draw_text(screen, self.engine, line,
                      bx + 24, by + 14 + i * 24, 17, C_TEXT)

        draw_text(screen, self.engine, "[SPACE] to close",
                  bx + box_w - 20, by + box_h - 24, 13,
                  C_TEXT_DIM, anchor="topright")

    # ── Choice menu ────────────────────────────────────────────────

    def _draw_choice(self, screen):
        # Find leader name
        leader_name = self.choice_npc or "Leader"

        box_w = 400
        item_h = 48
        box_h = len(self.choice_options) * item_h + 60
        bx = SCREEN_W // 2 - box_w // 2
        by = SCREEN_H // 2 - box_h // 2

        # Background
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((18, 22, 38, 240))
        screen.blit(bg, (bx, by))
        pygame.draw.rect(screen, C_ACCENT, (bx, by, box_w, box_h), 2,
                         border_radius=8)

        # Title
        draw_text(screen, self.engine, leader_name,
                  bx + box_w // 2, by + 12, 20,
                  C_ACCENT, anchor="midtop", bold=True)

        # Options
        labels = {
            'fight': "Fight Challenger Here",
            'upgrade': "Upgrade Team",
            'league': "View League Standings",
            'cancel': "Cancel",
        }
        colors = {
            'fight': C_RED,
            'upgrade': C_CYAN,
            'league': C_GREEN,
            'cancel': C_TEXT_DIM,
        }

        for i, opt in enumerate(self.choice_options):
            iy = by + 44 + i * item_h
            selected = (i == self.choice_selected)
            if selected:
                sel_bg = pygame.Surface((box_w - 16, item_h - 4),
                                        pygame.SRCALPHA)
                sel_bg.fill((55, 65, 105, 140))
                screen.blit(sel_bg, (bx + 8, iy))
                pygame.draw.rect(screen, C_ACCENT,
                                 (bx + 8, iy, box_w - 16, item_h - 4),
                                 1, border_radius=4)
            label = labels.get(opt, opt.title())
            col = colors.get(opt, C_TEXT)
            prefix = "> " if selected else "  "
            draw_text(screen, self.engine, prefix + label,
                      bx + 30, iy + 10, 19, col, bold=selected)

        # Hint
        draw_text(screen, self.engine, "UP/DOWN + SPACE | ESC to cancel",
                  bx + box_w // 2, by + box_h - 18, 12,
                  C_TEXT_DIM, anchor="midbottom")

    # ── Location label ─────────────────────────────────────────────

    def _draw_location(self, screen):
        label = self.game_map.name
        if label:
            draw_text(screen, self.engine, label,
                      SCREEN_W // 2, 52, 16, C_TEXT_DIM, anchor="midtop")
