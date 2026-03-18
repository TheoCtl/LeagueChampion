"""
Pokemon League Champion - Pygame Engine & UI Widgets
Core rendering, scene management, and reusable UI components.
"""
import os
import pygame
import sys

# ─── Constants ──────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1024, 768
FPS = 60

# Colors
C_BG = (24, 24, 32)
C_BG_LIGHT = (32, 36, 48)
C_PANEL = (40, 44, 58)
C_PANEL_BORDER = (70, 78, 100)
C_TEXT = (230, 230, 240)
C_TEXT_DIM = (140, 140, 160)
C_TEXT_BRIGHT = (255, 255, 255)
C_ACCENT = (80, 180, 255)
C_GOLD = (255, 210, 80)
C_GREEN = (80, 220, 120)
C_RED = (240, 70, 70)
C_YELLOW = (255, 220, 60)
C_HP_GREEN = (80, 220, 100)
C_HP_YELLOW = (230, 200, 50)
C_HP_RED = (220, 50, 50)
C_HP_BG = (50, 50, 60)
C_BTN = (55, 60, 80)
C_BTN_HOVER = (70, 80, 110)
C_BTN_BORDER = (90, 100, 130)
C_INPUT_BG = (30, 32, 44)
C_INPUT_BORDER = (80, 120, 200)

# Type colors
TYPE_COLORS = {
    "Normal": (168, 168, 120),
    "Fire": (240, 80, 48),
    "Water": (80, 144, 240),
    "Grass": (96, 200, 80),
    "Electric": (248, 208, 48),
    "Ice": (152, 216, 216),
    "Fighting": (192, 48, 40),
    "Poison": (160, 64, 160),
    "Ground": (224, 192, 104),
    "Flying": (168, 144, 240),
    "Psychic": (248, 88, 136),
    "Bug": (168, 184, 32),
    "Rock": (184, 160, 56),
    "Ghost": (112, 88, 152),
    "Dragon": (112, 56, 248),
    "Dark": (112, 88, 72),
    "Steel": (184, 184, 208),
    "Fairy": (238, 153, 172),
}


def type_color(type_name):
    return TYPE_COLORS.get(type_name, C_TEXT)


# ─── Engine ─────────────────────────────────────────────────────────

class Engine:
    """Main game engine: manages Pygame window and scene stack."""

    def __init__(self):
        pygame.init()
        # Get native display resolution for high-quality scaling
        info = pygame.display.Info()
        self.display_w = info.current_w
        self.display_h = info.current_h
        self.real_screen = pygame.display.set_mode(
            (self.display_w, self.display_h), pygame.FULLSCREEN)
        pygame.display.set_caption("Pokemon League Champion")
        # Logical render surface at base resolution
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
        # Font cache
        self._fonts = {}
        # Sprite cache
        self._sprites = {}

    def font(self, size):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("Segoe UI", size)
        return self._fonts[size]

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
                # Translate mouse coordinates from display to logical space
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

            # Smooth-scale logical surface to display
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
        self.anchor = anchor  # "topleft", "center", "midtop"
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
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=6)
        font = self._get_font(engine)
        surf = font.render(self.text, True, self.text_color)
        text_rect = surf.get_rect(center=self.rect.center)
        screen.blit(surf, text_rect)


class Panel:
    """A rectangular panel with optional title and border."""

    def __init__(self, x, y, w, h, title=None, bg=C_PANEL, border=C_PANEL_BORDER,
                 title_color=C_ACCENT):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.bg = bg
        self.border = border
        self.title_color = title_color

    def draw(self, screen, engine):
        pygame.draw.rect(screen, self.bg, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.border, self.rect, 2, border_radius=8)
        if self.title:
            font = engine.font(16)
            surf = font.render(self.title, True, self.title_color)
            tx = self.rect.x + 12
            ty = self.rect.y + 6
            screen.blit(surf, (tx, ty))


class HPBar:
    """Graphical HP bar."""

    def __init__(self, x, y, w, h, current, maximum):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.current = current
        self.maximum = maximum

    def set_hp(self, current, maximum):
        self.current = current
        self.maximum = maximum

    def draw(self, screen, engine):
        ratio = max(0, self.current / self.maximum) if self.maximum > 0 else 0
        if ratio > 0.5:
            color = C_HP_GREEN
        elif ratio > 0.2:
            color = C_HP_YELLOW
        else:
            color = C_HP_RED

        # Background
        pygame.draw.rect(screen, C_HP_BG, (self.x, self.y, self.w, self.h), border_radius=4)
        # Fill
        fill_w = max(0, int(self.w * ratio))
        if fill_w > 0:
            pygame.draw.rect(screen, color, (self.x, self.y, fill_w, self.h), border_radius=4)
        # Border
        pygame.draw.rect(screen, C_PANEL_BORDER, (self.x, self.y, self.w, self.h), 1, border_radius=4)
        # Text
        font = engine.font(14)
        text = f"{self.current}/{self.maximum}"
        surf = font.render(text, True, C_TEXT_BRIGHT)
        rect = surf.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
        screen.blit(surf, rect)


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
        border = C_INPUT_BORDER if self.focused else C_PANEL_BORDER
        pygame.draw.rect(screen, C_INPUT_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=6)
        font = engine.font(self.font_size)
        if self.text:
            surf = font.render(self.text, True, C_TEXT_BRIGHT)
        else:
            surf = font.render(self.placeholder, True, C_TEXT_DIM)
        text_rect = surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(surf, text_rect)
        # Cursor
        if self.focused and self.show_cursor:
            cx = text_rect.right + 2 if self.text else self.rect.x + 10
            pygame.draw.line(screen, C_ACCENT, (cx, self.rect.y + 6), (cx, self.rect.bottom - 6), 2)


class TypeBadge:
    """A small colored badge showing a Pokemon type."""

    def __init__(self, type_name, x, y, font_size=14):
        self.type_name = type_name
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = type_color(type_name)

    def draw(self, screen, engine):
        font = engine.font(self.font_size)
        surf = font.render(self.type_name, True, (255, 255, 255))
        tw, th = surf.get_size()
        pad_x, pad_y = 8, 3
        rect = pygame.Rect(self.x, self.y, tw + pad_x * 2, th + pad_y * 2)
        pygame.draw.rect(screen, self.color, rect, border_radius=4)
        screen.blit(surf, (self.x + pad_x, self.y + pad_y))
        return rect


class MessageLog:
    """Scrolling message log for battle text."""

    def __init__(self, x, y, w, h, max_messages=50, font_size=16):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []  # List of (text, color) tuples
        self.max_messages = max_messages
        self.font_size = font_size
        self.scroll = 0

    def add(self, text, color=C_TEXT):
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        # Auto-scroll to bottom
        self.scroll = max(0, len(self.messages) * (self.font_size + 4) - self.rect.h + 10)

    def clear(self):
        self.messages.clear()
        self.scroll = 0

    def draw(self, screen, engine):
        pygame.draw.rect(screen, C_BG_LIGHT, self.rect, border_radius=6)
        pygame.draw.rect(screen, C_PANEL_BORDER, self.rect, 1, border_radius=6)

        font = engine.font(self.font_size)
        line_h = self.font_size + 4
        clip = self.rect.inflate(-12, -8)
        screen.set_clip(clip)

        y = self.rect.y + 6 - self.scroll
        for text, color in self.messages:
            if y + line_h > self.rect.y - line_h and y < self.rect.bottom:
                surf = font.render(text, True, color)
                screen.blit(surf, (self.rect.x + 8, y))
            y += line_h

        screen.set_clip(None)


# ─── Helper draw functions ──────────────────────────────────────────

def draw_type_badges(screen, engine, types, x, y, font_size=14, gap=4):
    """Draw a row of type badges, return total width."""
    cx = x
    for t in types:
        badge = TypeBadge(t, cx, y, font_size)
        r = badge.draw(screen, engine)
        cx = r.right + gap
    return cx - x


def draw_text(screen, engine, text, x, y, size=18, color=C_TEXT, anchor="topleft"):
    """Quick text draw, returns the rect."""
    font = engine.font(size)
    surf = font.render(text, True, color)
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


def draw_pokemon_card(screen, engine, pokemon, x, y, w=280, show_moves=False):
    """Draw a compact Pokemon info card. Returns height used."""
    sprite_size = 40
    h = 70 if not show_moves else 70 + len(pokemon.moves) * 22 + 8
    panel = Panel(x, y, w, h)
    panel.draw(screen, engine)

    # Sprite + Name and level
    sx = x + 10
    draw_pokemon_sprite(screen, engine, pokemon.species, sx, y + 6, sprite_size)
    draw_text(screen, engine, f"{pokemon.species}  Lv.{pokemon.level}",
              sx + sprite_size + 6, y + 8, 18, C_TEXT_BRIGHT)

    # Types
    draw_type_badges(screen, engine, pokemon.types, x + 10, y + 32, 12)

    # HP bar
    hp = HPBar(x + 130, y + 32, w - 150, 18, pokemon.current_hp, pokemon.max_hp)
    hp.draw(screen, engine)

    if show_moves:
        my = y + 62
        for move_name in pokemon.moves:
            from data import MOVES_DB
            md = MOVES_DB.get(move_name, {})
            mtype = md.get("type", "Normal")
            mcolor = type_color(mtype)
            cat = "PHY" if md.get("category") == "physical" else "SPE"
            draw_text(screen, engine, f"  {move_name}  ({mtype} {cat} P:{md.get('power', '?')})",
                      x + 10, my, 14, mcolor)
            my += 22

    return h
