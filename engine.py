"""
Pokemon League Champion - Pygame Engine & UI Widgets
Pokemon B/W2 inspired visual style with rich colors and modern UI.
"""
import os
import pygame
import sys

# ─── Constants ──────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1920, 1080
FPS = 60

# ─── Color Palette (Pokemon B/W2 inspired) ──────────────────────────
C_BG = (18, 22, 38)
C_BG_LIGHT = (28, 34, 58)
C_BG_DARK = (10, 12, 22)
C_PANEL = (30, 36, 62)
C_PANEL_BORDER = (55, 65, 100)
C_PANEL_HIGHLIGHT = (42, 52, 85)
C_TEXT = (238, 240, 248)
C_TEXT_DIM = (145, 155, 180)
C_TEXT_BRIGHT = (255, 255, 255)
C_ACCENT = (68, 165, 255)
C_GOLD = (255, 200, 55)
C_GREEN = (50, 215, 100)
C_RED = (255, 60, 60)
C_YELLOW = (255, 218, 48)
C_CYAN = (80, 220, 240)
C_HP_GREEN = (58, 218, 88)
C_HP_YELLOW = (238, 200, 38)
C_HP_RED = (228, 48, 48)
C_HP_BG = (32, 35, 50)
C_HP_FRAME = (80, 90, 125)
C_BTN = (38, 46, 78)
C_BTN_HOVER = (55, 68, 108)
C_BTN_BORDER = (78, 90, 135)
C_INPUT_BG = (22, 25, 42)
C_INPUT_BORDER = (68, 115, 215)

# Battle colors
C_BATTLE_SKY_TOP = (128, 195, 250)
C_BATTLE_SKY_BOT = (72, 140, 215)
C_BATTLE_GROUND = (108, 165, 82)
C_BATTLE_GROUND_DARK = (75, 125, 58)
C_BATTLE_PLATFORM = (155, 125, 82)
C_BATTLE_PLATFORM_SHADOW = (110, 88, 58)
C_ACTION_PANEL = (22, 28, 48)
C_ACTION_BORDER = (48, 58, 92)

# ─── Type Colors ────────────────────────────────────────────────────
TYPE_COLORS = {
    "Normal":   (168, 168, 120),
    "Fire":     (245, 88, 48),
    "Water":    (88, 152, 245),
    "Grass":    (105, 205, 82),
    "Electric": (250, 212, 48),
    "Ice":      (148, 218, 218),
    "Fighting": (195, 52, 42),
    "Poison":   (165, 68, 165),
    "Ground":   (228, 195, 108),
    "Flying":   (172, 148, 242),
    "Psychic":  (252, 92, 140),
    "Bug":      (172, 188, 38),
    "Rock":     (188, 165, 58),
    "Ghost":    (115, 92, 158),
    "Dragon":   (115, 58, 252),
    "Dark":     (115, 92, 75),
    "Steel":    (188, 188, 212),
    "Fairy":    (242, 158, 178),
}


def type_color(type_name):
    return TYPE_COLORS.get(type_name, C_TEXT)


# ─── Engine ─────────────────────────────────────────────────────────

class Engine:
    """Main game engine: manages Pygame window and scene stack."""

    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.display_w = info.current_w
        self.display_h = info.current_h
        self.real_screen = pygame.display.set_mode(
            (self.display_w, self.display_h), pygame.FULLSCREEN)
        pygame.display.set_caption("Pokemon League Champion")
        # Logical render surface at 1920x1080
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        # Compute scale factor preserving aspect ratio
        scale = min(self.display_w / SCREEN_W, self.display_h / SCREEN_H)
        self.scaled_w = int(SCREEN_W * scale)
        self.scaled_h = int(SCREEN_H * scale)
        self.offset_x = (self.display_w - self.scaled_w) // 2
        self.offset_y = (self.display_h - self.scaled_h) // 2
        self._inv_scale = 1.0 / scale
        self.clock = pygame.time.Clock()
        self.scene = None
        self.running = True
        self._fonts = {}
        self._sprites = {}

    def font(self, size):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("Segoe UI", size)
        return self._fonts[size]

    def font_bold(self, size):
        key = ("bold", size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont("Segoe UI", size, bold=True)
        return self._fonts[key]

    def get_sprite(self, species, size=None):
        """Load and cache a Pokemon sprite. Returns Surface or None."""
        key = (species, size)
        if key not in self._sprites:
            path = os.path.join("sprites", f"{species}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.smoothscale(img, (size, size))
                self._sprites[key] = img
            else:
                self._sprites[key] = None
        return self._sprites[key]

    def get_trainer_sprite(self, name, size=None):
        """Load and cache a trainer sprite, preserving aspect ratio.
        `size` is the target height; width is scaled proportionally."""
        key = ("trainer", name, size)
        if key not in self._sprites:
            path = os.path.join("trainersprite", f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if size:
                    ow, oh = img.get_size()
                    ratio = ow / oh if oh > 0 else 1
                    new_h = size
                    new_w = max(1, int(size * ratio))
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                self._sprites[key] = img
            else:
                self._sprites[key] = None
        return self._sprites[key]

    def set_scene(self, scene):
        self.scene = scene
        self.scene.engine = self

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = []
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP):
                    mx = int((e.pos[0] - self.offset_x) * self._inv_scale)
                    my = int((e.pos[1] - self.offset_y) * self._inv_scale)
                    if e.type == pygame.MOUSEMOTION:
                        e = pygame.event.Event(
                            e.type, pos=(mx, my), rel=e.rel, buttons=e.buttons)
                    else:
                        e = pygame.event.Event(
                            e.type, pos=(mx, my), button=e.button)
                events.append(e)

            if self.scene:
                self.scene.handle_events(events)
                self.scene.update(dt)
                self.scene.draw(self.screen)

            self.real_screen.fill((0, 0, 0))
            scaled = pygame.transform.smoothscale(
                self.screen, (self.scaled_w, self.scaled_h))
            self.real_screen.blit(scaled, (self.offset_x, self.offset_y))
            pygame.display.flip()


class Scene:
    """Base scene class. Override handle_events, update, draw."""

    def __init__(self):
        self.engine = None

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(C_BG)


# ─── UI Widgets ─────────────────────────────────────────────────────

class Label:
    """Text label with optional color and alignment."""

    def __init__(self, text, x, y, font_size=20, color=C_TEXT, anchor="topleft"):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.anchor = anchor
        self._font = None

    def _get_font(self, engine):
        if self._font is None:
            self._font = engine.font(self.font_size)
        return self._font

    def draw(self, screen, engine):
        font = self._get_font(engine)
        surf = font.render(self.text, True, self.color)
        rect = surf.get_rect(**{self.anchor: (self.x, self.y)})
        screen.blit(surf, rect)
        return rect


class Button:
    """Clickable button with hover effect."""

    def __init__(self, text, x, y, w, h, callback=None, font_size=18,
                 color=C_BTN, hover_color=C_BTN_HOVER, text_color=C_TEXT,
                 border_color=C_BTN_BORDER, tag=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback
        self.font_size = font_size
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.tag = tag
        self.hovered = False
        self._font = None

    def _get_font(self, engine):
        if self._font is None:
            self._font = engine.font(self.font_size)
        return self._font

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def draw(self, screen, engine):
        color = self.hover_color if self.hovered else self.color
        # Shadow
        shadow = self.rect.move(3, 3)
        pygame.draw.rect(screen, (8, 10, 18), shadow, border_radius=10)
        # Background
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        # Highlight line at top
        if self.hovered:
            hl = pygame.Rect(self.rect.x + 4, self.rect.y + 2, self.rect.w - 8, 3)
            pygame.draw.rect(screen, self.border_color, hl, border_radius=2)
        # Border
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=10)
        # Text
        font = self._get_font(engine)
        surf = font.render(self.text, True, self.text_color)
        text_rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, text_rect)


class Panel:
    """A rectangular panel with optional title and border."""

    def __init__(self, x, y, w, h, title=None, bg=C_PANEL, border=C_PANEL_BORDER,
                 title_color=C_ACCENT, shadow=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.bg = bg
        self.border = border
        self.title_color = title_color
        self.shadow = shadow

    def draw(self, screen, engine):
        if self.shadow:
            sr = self.rect.move(4, 4)
            pygame.draw.rect(screen, (6, 8, 15), sr, border_radius=12)
        pygame.draw.rect(screen, self.bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, self.border, self.rect, 2, border_radius=12)
        if self.title:
            font = engine.font_bold(18)
            surf = font.render(self.title, True, self.title_color)
            tx = self.rect.x + 15
            ty = self.rect.y + 8
            screen.blit(surf, (tx, ty))


class HPBar:
    """Pokemon B/W2 style HP bar with 'HP' label."""

    def __init__(self, x, y, w, h, current, maximum, show_numbers=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.current = current
        self.maximum = maximum
        self.show_numbers = show_numbers

    def set_hp(self, current, maximum):
        self.current = current
        self.maximum = maximum

    def draw(self, screen, engine):
        ratio = max(0, self.current / self.maximum) if self.maximum > 0 else 0
        if ratio > 0.5:
            fill_color = C_HP_GREEN
        elif ratio > 0.2:
            fill_color = C_HP_YELLOW
        else:
            fill_color = C_HP_RED

        # "HP" label box
        label_w = max(30, self.h + 8)
        label_rect = pygame.Rect(self.x, self.y, label_w, self.h)
        pygame.draw.rect(screen, (55, 68, 95), label_rect, border_radius=4)
        pygame.draw.rect(screen, C_HP_FRAME, label_rect, 1, border_radius=4)
        hp_font = engine.font_bold(max(11, self.h - 8))
        hp_surf = hp_font.render("HP", True, (195, 225, 110))
        hp_rect = hp_surf.get_rect(center=label_rect.center)
        screen.blit(hp_surf, hp_rect)

        # Bar area
        bar_x = self.x + label_w + 3
        bar_w = self.w - label_w - 3
        bar_rect = pygame.Rect(bar_x, self.y, bar_w, self.h)

        # Background
        pygame.draw.rect(screen, C_HP_BG, bar_rect, border_radius=4)

        # Fill with slight gradient effect
        fill_w = max(0, int(bar_w * ratio))
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, self.y, fill_w, self.h)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)
            # Highlight strip at top of fill for a 3D look
            if self.h >= 12:
                hl_color = (min(255, fill_color[0] + 40),
                            min(255, fill_color[1] + 40),
                            min(255, fill_color[2] + 40))
                hl_rect = pygame.Rect(bar_x + 2, self.y + 2, max(0, fill_w - 4), 3)
                if hl_rect.w > 0:
                    pygame.draw.rect(screen, hl_color, hl_rect, border_radius=2)

        # Frame
        pygame.draw.rect(screen, C_HP_FRAME, bar_rect, 2, border_radius=4)

        # Numbers
        if self.show_numbers:
            num_font = engine.font(max(12, self.h - 6))
            num_text = f"{self.current} / {self.maximum}"
            num_surf = num_font.render(num_text, True, C_TEXT_BRIGHT)
            num_rect = num_surf.get_rect(center=(bar_x + bar_w // 2, self.y + self.h // 2))
            screen.blit(num_surf, num_rect)


class TextInput:
    """Simple single-line text input field."""

    def __init__(self, x, y, w, h, placeholder="", font_size=20, max_len=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.font_size = font_size
        self.max_len = max_len
        self.focused = True
        self.cursor_timer = 0
        self.show_cursor = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "submit"
            elif len(self.text) < self.max_len and event.unicode.isprintable() and event.unicode != "":
                self.text += event.unicode
        return None

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_timer = 0
            self.show_cursor = not self.show_cursor

    def draw(self, screen, engine):
        # Shadow
        sr = self.rect.move(2, 2)
        pygame.draw.rect(screen, (6, 8, 15), sr, border_radius=8)
        border = C_INPUT_BORDER if self.focused else C_PANEL_BORDER
        pygame.draw.rect(screen, C_INPUT_BG, self.rect, border_radius=8)
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=8)
        font = engine.font(self.font_size)
        if self.text:
            surf = font.render(self.text, True, C_TEXT_BRIGHT)
        else:
            surf = font.render(self.placeholder, True, C_TEXT_DIM)
        text_rect = surf.get_rect(midleft=(self.rect.x + 14, self.rect.centery))
        screen.blit(surf, text_rect)
        if self.focused and self.show_cursor:
            cx = text_rect.right + 2 if self.text else self.rect.x + 14
            pygame.draw.line(screen, C_ACCENT,
                             (cx, self.rect.y + 8), (cx, self.rect.bottom - 8), 2)


class TypeBadge:
    """A small colored badge showing a Pokemon type."""

    def __init__(self, type_name, x, y, font_size=14):
        self.type_name = type_name
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = type_color(type_name)

    def draw(self, screen, engine):
        font = engine.font_bold(self.font_size)
        surf = font.render(self.type_name, True, (255, 255, 255))
        tw, th = surf.get_size()
        pad_x, pad_y = 10, 4
        rect = pygame.Rect(self.x, self.y, tw + pad_x * 2, th + pad_y * 2)
        # Darker border for depth
        br = rect.inflate(2, 2)
        br.topleft = (rect.x - 1, rect.y - 1)
        pygame.draw.rect(screen, (max(0, self.color[0] - 40),
                                   max(0, self.color[1] - 40),
                                   max(0, self.color[2] - 40)), br, border_radius=5)
        pygame.draw.rect(screen, self.color, rect, border_radius=5)
        screen.blit(surf, (self.x + pad_x, self.y + pad_y))
        return rect


class MessageLog:
    """Scrolling message log for battle text."""

    def __init__(self, x, y, w, h, max_messages=60, font_size=18):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.max_messages = max_messages
        self.font_size = font_size
        self.scroll = 0

    def add(self, text, color=C_TEXT):
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.scroll = max(0, len(self.messages) * (self.font_size + 5) - self.rect.h + 14)

    def clear(self):
        self.messages.clear()
        self.scroll = 0

    def draw(self, screen, engine):
        # Shadow
        sr = self.rect.move(3, 3)
        pygame.draw.rect(screen, (5, 6, 12), sr, border_radius=10)
        # Background
        pygame.draw.rect(screen, (20, 25, 42), self.rect, border_radius=10)
        pygame.draw.rect(screen, C_ACTION_BORDER, self.rect, 2, border_radius=10)

        font = engine.font(self.font_size)
        line_h = self.font_size + 5
        clip = self.rect.inflate(-16, -12)
        screen.set_clip(clip)

        y = self.rect.y + 8 - self.scroll
        for text, color in self.messages:
            if y + line_h > self.rect.y - line_h and y < self.rect.bottom:
                surf = font.render(text, True, color)
                screen.blit(surf, (self.rect.x + 12, y))
            y += line_h

        screen.set_clip(None)


# ─── Helper Draw Functions ──────────────────────────────────────────

def draw_type_badges(screen, engine, types, x, y, font_size=14, gap=5):
    """Draw a row of type badges, return total width."""
    cx = x
    for t in types:
        badge = TypeBadge(t, cx, y, font_size)
        r = badge.draw(screen, engine)
        cx = r.right + gap
    return cx - x


def draw_text(screen, engine, text, x, y, size=18, color=C_TEXT, anchor="topleft",
              bold=False):
    """Quick text draw, returns the rect."""
    font = engine.font_bold(size) if bold else engine.font(size)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect(**{anchor: (x, y)})
    screen.blit(surf, rect)
    return rect


def draw_pokemon_sprite(screen, engine, species, x, y, size=24):
    """Draw a Pokemon sprite at (x, y). Returns width used (size or 0)."""
    spr = engine.get_sprite(species, size)
    if spr:
        screen.blit(spr, (x, y))
        return size
    return 0


def draw_trainer_sprite(screen, engine, name, x, y, size=24):
    """Draw a trainer sprite at (x, y). Returns width used."""
    spr = engine.get_trainer_sprite(name, size)
    if spr:
        screen.blit(spr, (x, y))
        return spr.get_width()
    return 0


def draw_pokeball_indicators(screen, team, x, y, size=16, gap=5):
    """Draw pokeball-style team health indicators."""
    for i, p in enumerate(team):
        cx = x + i * (size + gap) + size // 2
        cy = y + size // 2
        if p.is_fainted():
            pygame.draw.circle(screen, (65, 35, 35), (cx, cy), size // 2)
            pygame.draw.circle(screen, (140, 45, 45), (cx, cy), size // 2, 2)
            # X mark
            off = size // 4
            pygame.draw.line(screen, (180, 55, 55), (cx - off, cy - off),
                             (cx + off, cy + off), 2)
            pygame.draw.line(screen, (180, 55, 55), (cx + off, cy - off),
                             (cx - off, cy + off), 2)
        else:
            ratio = p.current_hp / p.max_hp if p.max_hp > 0 else 0
            if ratio > 0.5:
                color = C_HP_GREEN
                border = (40, 180, 70)
            elif ratio > 0.2:
                color = C_HP_YELLOW
                border = (200, 170, 30)
            else:
                color = C_HP_RED
                border = (190, 40, 40)
            pygame.draw.circle(screen, color, (cx, cy), size // 2)
            pygame.draw.circle(screen, border, (cx, cy), size // 2, 2)
            # Center dot
            pygame.draw.circle(screen, C_TEXT_BRIGHT, (cx, cy), max(2, size // 6))


def draw_status_badge(screen, engine, status, x, y):
    """Draw a status condition badge. Returns the rect."""
    from enums import Status1
    STATUS_INFO = {
        Status1.BURNED: ("BRN", (240, 80, 50)),
        Status1.POISONED: ("PSN", (170, 70, 200)),
        Status1.BADLY_POISONED: ("TOX", (150, 50, 180)),
        Status1.PARALYZED: ("PAR", (240, 200, 50)),
        Status1.ASLEEP: ("SLP", (130, 135, 155)),
        Status1.FROZEN: ("FRZ", (100, 205, 255)),
    }
    if status == Status1.NONE:
        return pygame.Rect(x, y, 0, 0)
    text, color = STATUS_INFO.get(status, ("???", C_TEXT_DIM))
    font = engine.font_bold(13)
    surf = font.render(text, True, (255, 255, 255))
    tw, th = surf.get_size()
    rect = pygame.Rect(x, y, tw + 12, th + 6)
    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, (min(255, color[0] + 30), min(255, color[1] + 30),
                               min(255, color[2] + 30)), rect, 1, border_radius=4)
    screen.blit(surf, (x + 6, y + 3))
    return rect


def draw_gradient_v(surface, rect, color_top, color_bot):
    """Draw a vertical gradient. Uses 1px-wide strip scaled for speed."""
    x, y, w, h = rect
    if h <= 0 or w <= 0:
        return
    strip = pygame.Surface((1, h))
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        strip.set_at((0, i), (r, g, b))
    scaled = pygame.transform.scale(strip, (w, h))
    surface.blit(scaled, (x, y))


def draw_pokemon_card(screen, engine, pokemon, x, y, w=400, show_moves=False):
    """Draw a compact Pokemon info card. Returns height used."""
    sprite_size = 52
    move_h = len(pokemon.moves) * 26 + 10 if show_moves else 0
    h = 80 + move_h
    panel = Panel(x, y, w, h, shadow=True)
    panel.draw(screen, engine)

    # Sprite + name + level
    sx = x + 12
    draw_pokemon_sprite(screen, engine, pokemon.species, sx, y + 8, sprite_size)
    draw_text(screen, engine, pokemon.species, sx + sprite_size + 10, y + 10,
              22, C_TEXT_BRIGHT, bold=True)
    draw_text(screen, engine, f"Lv.{pokemon.level}", sx + sprite_size + 10, y + 36,
              16, C_TEXT_DIM)

    # Types
    draw_type_badges(screen, engine, pokemon.types, x + 14, y + 44, 13)

    # HP bar
    hp = HPBar(x + 180, y + 42, w - 200, 22, pokemon.current_hp, pokemon.max_hp,
               show_numbers=True)
    hp.draw(screen, engine)

    if show_moves:
        my = y + 72
        for move_name in pokemon.moves:
            from data import MOVES_DB
            md = MOVES_DB.get(move_name, {})
            mtype = md.get("type", "Normal")
            mcolor = type_color(mtype)
            cat = md.get("category", "physical")
            cat_label = "PHY" if cat == "physical" else ("STA" if cat == "status" else "SPE")
            pw = md.get("power", 0)
            pw_str = str(pw) if pw else "—"
            # Small type dot
            pygame.draw.circle(screen, mcolor, (x + 22, my + 8), 5)
            draw_text(screen, engine,
                      f"{move_name}  ({cat_label} P:{pw_str})",
                      x + 32, my, 15, mcolor)
            my += 26

    return h
