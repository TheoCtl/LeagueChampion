"""
Pokemon League Champion - 2D World System
Fixed-camera rooms with procedural tile graphics, player character,
NPCs, roaming Pokemon, type-themed gyms, and the Champion hub.
"""
import pygame
import math
import random
from engine import TYPE_COLORS

# ─── Constants ──────────────────────────────────────────────────────

TILE_SIZE = 48
MAP_W = 40       # tiles wide  (40 × 48 = 1920)
MAP_H = 22       # tiles tall  (22 × 48 = 1056)
MAP_OFFSET_Y = 12  # center vertically in 1080: (1080-1056)//2
MOVE_DURATION = 0.15

# ─── Tile Definitions ──────────────────────────────────────────────

TILE_DEFS = {
    ' ':  {'walkable': False},
    '.':  {'walkable': True},          # stone floor
    'c':  {'walkable': True},          # carpet
    'w':  {'walkable': True},          # wood floor
    'd':  {'walkable': True},          # dark stone
    '#':  {'walkable': False},         # wall
    'X':  {'walkable': False},         # wall with torch
    'V':  {'walkable': False},         # wall with banner
    'W':  {'walkable': False},         # wall with window
    'P':  {'walkable': False},         # pillar
    'T':  {'walkable': False},         # throne / podium
    'K':  {'walkable': False},         # throne seat
    'B':  {'walkable': False},         # bookshelf
    'U':  {'walkable': False},         # table
    'Y':  {'walkable': False},         # trophy
    'O':  {'walkable': False},         # pokeball display
    'M':  {'walkable': False},         # statue
    'N':  {'walkable': False},         # sign post
    'R':  {'walkable': False},         # railing / fence
    '~':  {'walkable': False},         # liquid (water/lava/pool)
    'f':  {'walkable': True},          # type decoration on floor
}

# ─── Color Palette ──────────────────────────────────────────────────

C_STONE        = (148, 152, 162)
C_STONE_LINE   = (120, 124, 134)
C_STONE_LIGHT  = (165, 168, 178)
C_CARPET       = (170, 38, 48)
C_CARPET_DARK  = (138, 28, 35)
C_CARPET_GOLD  = (218, 178, 52)
C_WOOD         = (152, 112, 72)
C_WOOD_DARK    = (122, 88, 55)
C_WOOD_LINE    = (112, 80, 50)
C_WALL         = (72, 80, 92)
C_WALL_DARK    = (55, 60, 72)
C_WALL_MORTAR  = (60, 68, 78)
C_WALL_LIGHT   = (88, 95, 108)
C_PILLAR       = (168, 172, 182)
C_PILLAR_DARK  = (128, 132, 142)
C_PILLAR_LIGHT = (195, 198, 208)
C_WATER        = (68, 135, 210)
C_WATER_LIGHT  = (95, 165, 235)

C_SKIN         = (255, 212, 172)
C_HAIR         = (48, 40, 58)
C_COAT         = (188, 38, 45)
C_COAT_DARK    = (148, 28, 35)
C_COAT_GOLD    = (238, 198, 58)
C_PANTS        = (45, 45, 65)
C_SHOES        = (65, 40, 30)


# ═══════════════════════════════════════════════════════════════════
#  Color helpers
# ═══════════════════════════════════════════════════════════════════

def _clamp(v):
    return max(0, min(255, int(v)))

def _tint(base, target, strength=0.35):
    return tuple(_clamp(b + (t - b) * strength) for b, t in zip(base, target))

def _darken(c, f=0.75):
    return tuple(_clamp(v * f) for v in c)

def _lighten(c, f=1.25):
    return tuple(_clamp(v * f) for v in c)


# ═══════════════════════════════════════════════════════════════════
#  Themed Tile Set
# ═══════════════════════════════════════════════════════════════════

class ThemedTileSet:
    """Generates tile surfaces tinted by a type accent color."""

    def __init__(self, accent=(148, 152, 162), seed=42):
        self.accent = accent
        self.rng = random.Random(seed)
        self._tiles = {}
        self._generate()

    def get(self, char):
        return self._tiles.get(char, self._tiles.get(' '))

    def _generate(self):
        s = TILE_SIZE
        a = self.accent
        rng = self.rng

        # void
        surf = pygame.Surface((s, s))
        surf.fill((0, 0, 0))
        self._tiles[' '] = surf

        self._tiles['.'] = self._floor(rng, C_STONE, C_STONE_LINE)
        self._tiles['d'] = self._floor(rng, _darken(C_STONE, 0.68),
                                        _darken(C_STONE_LINE, 0.68))
        self._tiles['c'] = self._carpet(a)
        self._tiles['w'] = self._wood(rng)
        wc = _tint(C_WALL, a, 0.15)
        self._tiles['#'] = self._wall(wc)
        self._tiles['X'] = self._wall_torch(wc, a)
        self._tiles['V'] = self._wall_banner(wc, a)
        self._tiles['W'] = self._wall_window(wc)
        self._tiles['P'] = self._pillar(rng)
        self._tiles['T'] = self._podium(a)
        self._tiles['K'] = self._throne(a)
        self._tiles['B'] = self._bookshelf(rng)
        self._tiles['U'] = self._table(rng)
        self._tiles['Y'] = self._trophy(rng)
        self._tiles['O'] = self._pokeball(rng)
        self._tiles['M'] = self._statue(rng)
        self._tiles['N'] = self._sign(rng)
        self._tiles['R'] = self._railing(rng)
        self._tiles['~'] = self._liquid(rng, a)
        self._tiles['f'] = self._deco(rng, a)

    # ── helpers ─────────────────────────────────────────────────────

    def _floor(self, rng, base, line):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill(base)
        pygame.draw.line(surf, line, (0, 0), (s, 0), 1)
        pygame.draw.line(surf, line, (0, 0), (0, s), 1)
        pygame.draw.line(surf, line, (s // 2, 0), (s // 2, s), 1)
        pygame.draw.line(surf, line, (0, s // 2), (s, s // 2), 1)
        for _ in range(3):
            surf.set_at((rng.randint(2, s - 3), rng.randint(2, s - 3)),
                        rng.choice([line, _lighten(base)]))
        return surf

    def _carpet(self, accent):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill(accent)
        pygame.draw.rect(surf, _darken(accent, 0.8), (0, 0, s, s), 2)
        pygame.draw.rect(surf, C_CARPET_GOLD, (3, 3, s - 6, s - 6), 1)
        cx, cy = s // 2, s // 2
        pts = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
        pygame.draw.polygon(surf, _darken(accent, 0.75), pts, 1)
        return surf

    def _wood(self, rng):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill(C_WOOD)
        for y in range(0, s, 12):
            pygame.draw.line(surf, C_WOOD_LINE, (0, y), (s, y), 1)
            off = ((y // 12) % 2) * (s // 2)
            pygame.draw.line(surf, C_WOOD_LINE, (off + s // 4, y),
                             (off + s // 4, min(y + 12, s)), 1)
        return surf

    def _wall(self, wc):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill(wc)
        bh = 12
        mortar = _darken(wc, 0.82)
        for row in range(s // bh + 1):
            y = row * bh
            off = (row % 2) * (s // 2)
            pygame.draw.line(surf, mortar, (0, y), (s, y), 1)
            for x in range(off, s + s, s // 2):
                if 0 <= x < s:
                    pygame.draw.line(surf, mortar, (x, y),
                                     (x, min(y + bh, s)), 1)
        pygame.draw.line(surf, _lighten(wc, 1.15), (0, 1), (s, 1), 1)
        pygame.draw.line(surf, _darken(wc, 0.7), (0, s - 1), (s, s - 1), 2)
        return surf

    def _wall_torch(self, wc, accent):
        s = TILE_SIZE
        surf = self._wall(wc).copy()
        pygame.draw.rect(surf, (125, 82, 42), (s // 2 - 3, s // 2 - 6, 6, 14))
        pygame.draw.ellipse(surf, (255, 185, 42),
                            (s // 2 - 5, s // 2 - 14, 10, 12))
        pygame.draw.ellipse(surf, _lighten(accent),
                            (s // 2 - 3, s // 2 - 12, 6, 8))
        glow = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*accent[:3], 35), (s // 2, s // 2 - 6), 18)
        surf.blit(glow, (0, 0))
        return surf

    def _wall_banner(self, wc, accent):
        s = TILE_SIZE
        surf = self._wall(wc).copy()
        pygame.draw.rect(surf, (182, 162, 122), (s // 2 - 12, 4, 24, 3))
        pts = [(s // 2 - 10, 7), (s // 2 + 10, 7),
               (s // 2 + 8, s - 8), (s // 2, s - 4), (s // 2 - 8, s - 8)]
        pygame.draw.polygon(surf, accent, pts)
        pygame.draw.polygon(surf, C_CARPET_GOLD, pts, 2)
        pygame.draw.circle(surf, C_CARPET_GOLD, (s // 2, s // 2 + 2), 5, 1)
        return surf

    def _wall_window(self, wc):
        s = TILE_SIZE
        surf = self._wall(wc).copy()
        wx, wy, ww, wh = s // 2 - 8, 6, 16, 24
        pygame.draw.rect(surf, (62, 52, 42), (wx - 1, wy - 1, ww + 2, wh + 2))
        pygame.draw.rect(surf, (132, 198, 248), (wx, wy, ww, wh))
        pygame.draw.line(surf, (62, 52, 42), (s // 2, wy),
                         (s // 2, wy + wh), 2)
        pygame.draw.line(surf, (62, 52, 42), (wx, wy + wh // 2),
                         (wx + ww, wy + wh // 2), 2)
        return surf

    def _pillar(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        px, pw = s // 2 - 8, 16
        pygame.draw.rect(surf, C_PILLAR, (px, 0, pw, s))
        pygame.draw.rect(surf, C_PILLAR_DARK, (px, 0, 5, s))
        pygame.draw.rect(surf, C_PILLAR_LIGHT, (px + pw - 5, 0, 5, s))
        pygame.draw.rect(surf, C_PILLAR_LIGHT, (px - 3, 0, pw + 6, 6))
        pygame.draw.rect(surf, C_PILLAR_DARK, (px - 3, 0, pw + 6, 6), 1)
        pygame.draw.rect(surf, C_PILLAR_LIGHT, (px - 2, s - 6, pw + 4, 6))
        pygame.draw.rect(surf, C_PILLAR_DARK, (px - 2, s - 6, pw + 4, 6), 1)
        return surf

    def _podium(self, accent):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill(_tint((128, 118, 102), accent, 0.2))
        pygame.draw.rect(surf, _darken(accent, 0.65), (0, 0, s, s), 2)
        pygame.draw.rect(surf, C_CARPET_GOLD, (2, 2, s - 4, s - 4), 1)
        return surf

    def _throne(self, accent):
        s = TILE_SIZE
        surf = self._podium(accent).copy()
        pygame.draw.rect(surf, accent, (s // 2 - 10, 0, 20, 22))
        pygame.draw.rect(surf, C_CARPET_GOLD, (s // 2 - 10, 0, 20, 22), 2)
        pts = [(s // 2 - 6, 4), (s // 2 - 3, 0),
               (s // 2, 3), (s // 2 + 3, 0), (s // 2 + 6, 4)]
        pygame.draw.polygon(surf, C_CARPET_GOLD, pts)
        pygame.draw.rect(surf, _darken(accent, 0.7), (s // 2 - 8, 22, 16, 12))
        return surf

    def _bookshelf(self, rng):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        surf.fill((82, 60, 40))
        for y in [0, s // 3, 2 * s // 3]:
            pygame.draw.rect(surf, C_WOOD, (0, y, s, 4))
        book_colors = [(168, 48, 48), (48, 88, 168), (48, 148, 68),
                       (188, 148, 48), (148, 48, 148), (48, 148, 168),
                       (198, 78, 48), (78, 168, 58)]
        for shelf_y in [4, s // 3 + 4, 2 * s // 3 + 4]:
            x = 4
            for _ in range(6):
                bw = rng.randint(4, 7)
                col = rng.choice(book_colors)
                pygame.draw.rect(surf, col, (x, shelf_y, bw, s // 3 - 7))
                x += bw + 1
                if x > s - 6:
                    break
        pygame.draw.rect(surf, C_WOOD_DARK, (0, 0, s, s), 2)
        return surf

    def _table(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, C_WOOD, (4, 8, s - 8, s - 16))
        pygame.draw.rect(surf, C_WOOD_DARK, (4, 8, s - 8, s - 16), 2)
        return surf

    def _trophy(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, (158, 150, 140), (s // 2 - 10, s - 14, 20, 14))
        pygame.draw.rect(surf, C_CARPET_GOLD, (s // 2 - 6, 14, 12, 18))
        pygame.draw.rect(surf, (238, 198, 58), (s // 2 - 8, 10, 16, 8))
        pygame.draw.circle(surf, (255, 248, 182), (s // 2, 16), 3)
        return surf

    def _pokeball(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, (82, 82, 92),
                         (s // 2 - 8, s // 2 + 2, 16, s // 2 - 2))
        pygame.draw.rect(surf, (98, 98, 108), (s // 2 - 10, s // 2, 20, 4))
        pygame.draw.circle(surf, (232, 42, 42), (s // 2, s // 2 - 6), 10)
        pygame.draw.rect(surf, (242, 242, 248),
                         (s // 2 - 10, s // 2 - 6, 20, 11))
        pygame.draw.circle(surf, (42, 42, 48), (s // 2, s // 2 - 6), 10, 1)
        pygame.draw.line(surf, (42, 42, 48),
                         (s // 2 - 10, s // 2 - 6),
                         (s // 2 + 10, s // 2 - 6), 2)
        pygame.draw.circle(surf, (242, 242, 248), (s // 2, s // 2 - 6), 4)
        pygame.draw.circle(surf, (42, 42, 48), (s // 2, s // 2 - 6), 4, 1)
        pygame.draw.circle(surf, (242, 242, 248), (s // 2, s // 2 - 6), 2)
        return surf

    def _statue(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, (142, 142, 152), (s // 2 - 10, s - 12, 20, 12))
        pygame.draw.ellipse(surf, (162, 162, 172), (s // 2 - 8, 10, 16, 26))
        pygame.draw.circle(surf, (172, 172, 182), (s // 2, 12), 8)
        pygame.draw.circle(surf, (132, 132, 142), (s // 2, 12), 8, 1)
        return surf

    def _sign(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, C_WOOD_DARK, (s // 2 - 2, s // 2, 4, s // 2))
        pygame.draw.rect(surf, C_WOOD, (s // 2 - 12, 8, 24, 18))
        pygame.draw.rect(surf, C_WOOD_DARK, (s // 2 - 12, 8, 24, 18), 2)
        pygame.draw.line(surf, (200, 185, 155),
                         (s // 2 - 8, 14), (s // 2 + 8, 14), 1)
        pygame.draw.line(surf, (200, 185, 155),
                         (s // 2 - 6, 19), (s // 2 + 6, 19), 1)
        return surf

    def _railing(self, rng):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        pygame.draw.rect(surf, C_WOOD, (0, s // 2 - 4, s, 8))
        pygame.draw.rect(surf, C_WOOD_DARK, (0, s // 2 - 4, s, 8), 1)
        for x in [4, s - 8]:
            pygame.draw.rect(surf, C_WOOD_DARK, (x, s // 2 - 8, 4, 16))
        return surf

    def _liquid(self, rng, accent):
        s = TILE_SIZE
        surf = pygame.Surface((s, s))
        base = _tint(C_WATER, accent, 0.5)
        surf.fill(base)
        hi = _lighten(base, 1.3)
        for y in range(0, s, 8):
            for x in range(0, s, 12):
                ox = rng.randint(-2, 2)
                pygame.draw.arc(surf, hi, (x + ox, y, 10, 6), 0, 3.14, 1)
        return surf

    def _deco(self, rng, accent):
        s = TILE_SIZE
        surf = self._floor(rng, C_STONE, C_STONE_LINE).copy()
        light = _lighten(accent, 1.3)
        for _ in range(5):
            fx = rng.randint(4, s - 6)
            fy = rng.randint(4, s - 6)
            pygame.draw.circle(surf, accent, (fx, fy), 3)
            pygame.draw.circle(surf, light, (fx, fy), 1)
        return surf


# ═══════════════════════════════════════════════════════════════════
#  Player Sprite Generation
# ═══════════════════════════════════════════════════════════════════

def _generate_player_sprites():
    sprites = {}
    for d in ('down', 'up', 'left', 'right'):
        for f in range(3):
            sprites[(d, f)] = _draw_player(d, f)
    return sprites


def _draw_player(direction, frame):
    s = TILE_SIZE
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    bob = -1 if frame in (1, 2) else 0
    lp = {0: 0, 1: -1, 2: 1}[frame]
    cx = s // 2
    if direction == 'down':
        _draw_front(surf, cx, bob, lp)
    elif direction == 'up':
        _draw_back(surf, cx, bob, lp)
    elif direction == 'left':
        _draw_side(surf, cx, bob, lp, False)
    elif direction == 'right':
        _draw_side(surf, cx, bob, lp, True)
    return surf


def _draw_front(surf, cx, bob, lp):
    y = bob
    pygame.draw.rect(surf, C_COAT_DARK, (cx - 11, 16 + y, 22, 18))
    pygame.draw.ellipse(surf, C_HAIR, (cx - 9, 2 + y, 18, 16))
    pygame.draw.ellipse(surf, C_SKIN, (cx - 7, 5 + y, 14, 12))
    pygame.draw.ellipse(surf, C_HAIR, (cx - 8, 2 + y, 16, 8))
    pygame.draw.rect(surf, (32, 32, 58), (cx - 5, 10 + y, 3, 3))
    pygame.draw.rect(surf, (32, 32, 58), (cx + 2, 10 + y, 3, 3))
    pygame.draw.rect(surf, (255, 255, 255), (cx - 4, 10 + y, 1, 1))
    pygame.draw.rect(surf, (255, 255, 255), (cx + 3, 10 + y, 1, 1))
    pygame.draw.rect(surf, C_COAT, (cx - 9, 17 + y, 18, 14))
    pygame.draw.rect(surf, C_COAT_GOLD, (cx - 1, 19 + y, 2, 2))
    pygame.draw.rect(surf, C_COAT_GOLD, (cx - 1, 24 + y, 2, 2))
    pygame.draw.line(surf, C_COAT_GOLD,
                     (cx - 9, 17 + y), (cx - 4, 20 + y), 2)
    pygame.draw.line(surf, C_COAT_GOLD,
                     (cx + 9, 17 + y), (cx + 4, 20 + y), 2)
    pygame.draw.rect(surf, C_COAT, (cx - 12, 18 + y, 4, 10))
    pygame.draw.rect(surf, C_COAT, (cx + 8, 18 + y, 4, 10))
    pygame.draw.rect(surf, C_SKIN, (cx - 12, 27 + y, 4, 3))
    pygame.draw.rect(surf, C_SKIN, (cx + 8, 27 + y, 4, 3))
    lo = lp * 3
    pygame.draw.rect(surf, C_PANTS, (cx - 6 + lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_PANTS, (cx + 1 - lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_SHOES, (cx - 7 + lo, 39 + y, 7, 4))
    pygame.draw.rect(surf, C_SHOES, (cx + 0 - lo, 39 + y, 7, 4))


def _draw_back(surf, cx, bob, lp):
    y = bob
    pts = [(cx - 12, 15 + y), (cx + 12, 15 + y),
           (cx + 14, 34 + y), (cx - 14, 34 + y)]
    pygame.draw.polygon(surf, C_COAT, pts)
    pygame.draw.polygon(surf, C_COAT_DARK, pts, 2)
    pygame.draw.line(surf, C_COAT_GOLD,
                     (cx - 14, 34 + y), (cx + 14, 34 + y), 2)
    pygame.draw.ellipse(surf, C_HAIR, (cx - 9, 2 + y, 18, 16))
    pygame.draw.rect(surf, C_COAT, (cx - 9, 15 + y, 18, 8))
    pygame.draw.line(surf, C_COAT_GOLD,
                     (cx - 9, 15 + y), (cx + 9, 15 + y), 2)
    lo = lp * 3
    pygame.draw.rect(surf, C_PANTS, (cx - 6 + lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_PANTS, (cx + 1 - lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_SHOES, (cx - 7 + lo, 39 + y, 7, 4))
    pygame.draw.rect(surf, C_SHOES, (cx + 0 - lo, 39 + y, 7, 4))


def _draw_side(surf, cx, bob, lp, flip):
    y = bob
    dx = 2 if not flip else -2
    if flip:
        pygame.draw.rect(surf, C_COAT_DARK, (cx - 14, 15 + y, 12, 19))
        pygame.draw.line(surf, C_COAT_GOLD,
                         (cx - 14, 33 + y), (cx - 2, 33 + y), 2)
    else:
        pygame.draw.rect(surf, C_COAT_DARK, (cx + 2, 15 + y, 12, 19))
        pygame.draw.line(surf, C_COAT_GOLD,
                         (cx + 2, 33 + y), (cx + 14, 33 + y), 2)
    pygame.draw.ellipse(surf, C_HAIR, (cx - 8 + dx, 2 + y, 16, 16))
    if flip:
        pygame.draw.ellipse(surf, C_SKIN, (cx - 2, 5 + y, 12, 11))
        pygame.draw.rect(surf, (32, 32, 58), (cx + 4, 9 + y, 3, 3))
        pygame.draw.rect(surf, (255, 255, 255), (cx + 5, 9 + y, 1, 1))
    else:
        pygame.draw.ellipse(surf, C_SKIN, (cx - 10, 5 + y, 12, 11))
        pygame.draw.rect(surf, (32, 32, 58), (cx - 7, 9 + y, 3, 3))
        pygame.draw.rect(surf, (255, 255, 255), (cx - 6, 9 + y, 1, 1))
    pygame.draw.rect(surf, C_COAT, (cx - 7 + dx, 17 + y, 14, 14))
    bx = cx + 2 if flip else cx - 4
    pygame.draw.rect(surf, C_COAT_GOLD, (bx, 20 + y, 2, 2))
    ax = cx + 5 + dx if flip else cx - 9 + dx
    pygame.draw.rect(surf, C_COAT, (ax, 18 + y, 4, 10))
    pygame.draw.rect(surf, C_SKIN, (ax, 27 + y, 4, 3))
    lo = lp * 3
    pygame.draw.rect(surf, C_PANTS, (cx - 4 + dx + lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_PANTS, (cx + 1 + dx - lo, 31 + y, 5, 9))
    pygame.draw.rect(surf, C_SHOES, (cx - 5 + dx + lo, 39 + y, 7, 4))
    pygame.draw.rect(surf, C_SHOES, (cx + 0 + dx - lo, 39 + y, 7, 4))


# ═══════════════════════════════════════════════════════════════════
#  NPC Fallback Sprite
# ═══════════════════════════════════════════════════════════════════

def _make_npc_fallback(name):
    s = TILE_SIZE
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    h = hash(name) % 360
    r = max(80, (h * 7 + 50) % 200 + 55)
    g = max(80, (h * 13 + 100) % 200 + 55)
    b = max(80, (h * 19 + 150) % 200 + 55)
    pygame.draw.ellipse(surf, (r, g, b), (8, 12, 32, 28))
    pygame.draw.circle(surf, C_SKIN, (s // 2, 12), 10)
    pygame.draw.ellipse(surf, (60, 50, 70), (s // 2 - 8, 2, 16, 12))
    pygame.draw.rect(surf, (30, 30, 50), (s // 2 - 4, 10, 2, 2))
    pygame.draw.rect(surf, (30, 30, 50), (s // 2 + 2, 10, 2, 2))
    return surf


# ═══════════════════════════════════════════════════════════════════
#  Player, NPC, RoamingPokemon
# ═══════════════════════════════════════════════════════════════════

class Player:
    """Grid-based player with smooth movement interpolation."""

    def __init__(self, gx, gy):
        self.grid_x = gx
        self.grid_y = gy
        self.pixel_x = float(gx * TILE_SIZE)
        self.pixel_y = float(gy * TILE_SIZE)
        self.direction = 'down'
        self.moving = False
        self.target_gx = gx
        self.target_gy = gy
        self.move_progress = 0.0
        self.frame = 0
        self.frame_timer = 0.0
        self.sprites = _generate_player_sprites()

    @property
    def center_x(self):
        return self.pixel_x + TILE_SIZE // 2

    @property
    def center_y(self):
        return self.pixel_y + TILE_SIZE // 2

    def try_move(self, direction, game_map):
        if self.moving:
            return False
        dx, dy = {'up': (0, -1), 'down': (0, 1),
                  'left': (-1, 0), 'right': (1, 0)}[direction]
        nx, ny = self.grid_x + dx, self.grid_y + dy
        self.direction = direction
        if nx < 0 or ny < 0 or nx >= game_map.width or ny >= game_map.height:
            return False
        if not game_map.is_walkable(nx, ny):
            return False
        self.target_gx = nx
        self.target_gy = ny
        self.moving = True
        self.move_progress = 0.0
        return True

    def update(self, dt):
        if self.moving:
            self.move_progress += dt / MOVE_DURATION
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.grid_x = self.target_gx
                self.grid_y = self.target_gy
                self.moving = False
            sx = self.grid_x * TILE_SIZE
            sy = self.grid_y * TILE_SIZE
            ex = self.target_gx * TILE_SIZE
            ey = self.target_gy * TILE_SIZE
            t = self.move_progress
            t = t * t * (3 - 2 * t)
            self.pixel_x = sx + (ex - sx) * t
            self.pixel_y = sy + (ey - sy) * t
            self.frame_timer += dt
            if self.frame_timer >= 0.12:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % 3
        else:
            self.pixel_x = float(self.grid_x * TILE_SIZE)
            self.pixel_y = float(self.grid_y * TILE_SIZE)
            self.frame = 0

    def get_sprite(self):
        return self.sprites.get((self.direction, self.frame))

    def facing_tile(self):
        dx, dy = {'up': (0, -1), 'down': (0, 1),
                  'left': (-1, 0), 'right': (1, 0)}[self.direction]
        return self.grid_x + dx, self.grid_y + dy


class NPC:
    """Non-player character with trainer sprite and dialogue."""

    def __init__(self, gx, gy, name, direction='down',
                 dialogue="...", sprite_name=None, role=None):
        self.grid_x = gx
        self.grid_y = gy
        self.name = name
        self.direction = direction
        self.dialogue = dialogue
        self.sprite_name = sprite_name
        self.role = role
        self._sprite = None
        self._fallback = None

    def get_sprite(self, engine, size=None):
        sz = size or TILE_SIZE
        if self._sprite is None:
            if self.sprite_name:
                self._sprite = engine.get_trainer_sprite(self.sprite_name, sz)
            if self._sprite is None:
                self._fallback = _make_npc_fallback(self.name)
        return self._sprite or self._fallback


class RoamingPokemon:
    """A Pokemon that wanders randomly in the gym."""

    def __init__(self, species, gx, gy):
        self.species = species
        self.grid_x = gx
        self.grid_y = gy
        self.pixel_x = float(gx * TILE_SIZE)
        self.pixel_y = float(gy * TILE_SIZE)
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.moving = False
        self.target_gx = gx
        self.target_gy = gy
        self.move_progress = 0.0
        self.idle_timer = random.uniform(1.0, 3.0)
        self._sprite = None

    def update(self, dt, game_map, occupied):
        if self.moving:
            self.move_progress += dt / 0.3
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.grid_x = self.target_gx
                self.grid_y = self.target_gy
                self.moving = False
                self.idle_timer = random.uniform(1.5, 4.0)
            sx = (self.grid_x if not self.moving else self.grid_x) * TILE_SIZE
            sy = self.grid_y * TILE_SIZE
            ex = self.target_gx * TILE_SIZE
            ey = self.target_gy * TILE_SIZE
            t = self.move_progress
            t = t * t * (3 - 2 * t)
            self.pixel_x = sx + (ex - sx) * t
            self.pixel_y = sy + (ey - sy) * t
        else:
            self.pixel_x = float(self.grid_x * TILE_SIZE)
            self.pixel_y = float(self.grid_y * TILE_SIZE)
            self.idle_timer -= dt
            if self.idle_timer <= 0:
                self._try_wander(game_map, occupied)

    def _try_wander(self, game_map, occupied):
        dirs = ['up', 'down', 'left', 'right']
        random.shuffle(dirs)
        for d in dirs:
            dx, dy = {'up': (0, -1), 'down': (0, 1),
                      'left': (-1, 0), 'right': (1, 0)}[d]
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if (0 <= nx < game_map.width and 0 <= ny < game_map.height
                    and game_map.is_walkable(nx, ny)
                    and (nx, ny) not in occupied):
                self.direction = d
                self.target_gx = nx
                self.target_gy = ny
                self.moving = True
                self.move_progress = 0.0
                return
        self.idle_timer = random.uniform(1.0, 2.0)

    def get_sprite(self, engine):
        if self._sprite is None:
            self._sprite = engine.get_sprite(self.species, TILE_SIZE)
        return self._sprite


# ═══════════════════════════════════════════════════════════════════
#  Game Map
# ═══════════════════════════════════════════════════════════════════

class GameMap:
    """Tile-based room map with collision, interactions, and doors."""

    def __init__(self, tile_data, npcs=None, roaming=None,
                 name="", tileset=None, doors=None):
        self.name = name
        max_w = max(len(row) for row in tile_data) if tile_data else 0
        self.tile_data = [row.ljust(max_w) for row in tile_data]
        self.height = len(self.tile_data)
        self.width = max_w
        self.npcs = npcs or []
        self.roaming = roaming or []
        self.doors = doors or {}        # {(x,y): "door_target_id"}
        self.interactions = {}

        # Collision map
        self.collision = []
        for y, row in enumerate(self.tile_data):
            cr = []
            for x in range(self.width):
                char = row[x] if x < len(row) else ' '
                td = TILE_DEFS.get(char, {'walkable': False})
                cr.append(td.get('walkable', False))
            self.collision.append(cr)

        # Door tiles are walkable (player steps on them to trigger)
        for dx, dy in self.doors:
            if 0 <= dy < self.height and 0 <= dx < self.width:
                self.collision[dy][dx] = True

        # Mark NPC tiles as non-walkable
        for npc in self.npcs:
            if 0 <= npc.grid_y < self.height and 0 <= npc.grid_x < self.width:
                self.collision[npc.grid_y][npc.grid_x] = False

        # Build interaction map
        # Door interactions (standing on the tile)
        for (dx, dy), target in self.doors.items():
            self.interactions[(dx, dy)] = f"door:{target}"

        # NPC interactions (facing the NPC from adjacent walkable tile)
        for npc in self.npcs:
            for ddx, ddy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ix, iy = npc.grid_x + ddx, npc.grid_y + ddy
                if 0 <= ix < self.width and 0 <= iy < self.height:
                    if self.collision[iy][ix]:
                        self.interactions[(ix, iy)] = f"npc:{npc.name}"

        # Tileset & pre-render
        self.tileset = tileset or ThemedTileSet()
        self._rendered = None
        # Door tile overrides (set externally for champion room)
        self._door_tiles = {}
        self._door_labels = {}

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.collision[y][x]
        return False

    def render(self):
        if self._rendered is None:
            self._rendered = pygame.Surface(
                (self.width * TILE_SIZE, self.height * TILE_SIZE))
            for y, row in enumerate(self.tile_data):
                for x in range(self.width):
                    char = row[x] if x < len(row) else ' '
                    # Check for door tile override
                    if (x, y) in self._door_tiles:
                        self._rendered.blit(self._door_tiles[(x, y)],
                                            (x * TILE_SIZE, y * TILE_SIZE))
                    else:
                        t = self.tileset.get(char)
                        self._rendered.blit(t, (x * TILE_SIZE, y * TILE_SIZE))
        return self._rendered

    def get_interaction(self, x, y):
        return self.interactions.get((x, y))

    def get_npc_by_name(self, name):
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None

    def pixel_width(self):
        return self.width * TILE_SIZE

    def pixel_height(self):
        return self.height * TILE_SIZE


# ═══════════════════════════════════════════════════════════════════
#  Door tile builder
# ═══════════════════════════════════════════════════════════════════

def _make_door_tile(accent, is_current=False):
    """Create a gym entrance door tile with type-colored theme."""
    s = TILE_SIZE
    surf = pygame.Surface((s, s))
    surf.fill(_darken(accent, 0.6))
    # Door body
    pygame.draw.rect(surf, accent, (4, 2, s - 8, s - 4))
    pygame.draw.rect(surf, _lighten(accent), (4, 2, s - 8, s - 4), 2)
    # Panel lines
    pygame.draw.rect(surf, _darken(accent, 0.7), (8, 6, s - 16, 14))
    pygame.draw.rect(surf, _darken(accent, 0.7), (8, 24, s - 16, 14))
    # Doorknob
    pygame.draw.circle(surf, C_CARPET_GOLD, (s - 14, s // 2), 3)
    # Glowing border if this is the current challenger gym
    if is_current:
        pygame.draw.rect(surf, (255, 255, 100), (2, 0, s - 4, s), 3)
    return surf


# ═══════════════════════════════════════════════════════════════════
#  Champion Room (Hub)
# ═══════════════════════════════════════════════════════════════════

def build_champion_room(league_members=None, challenger_position=0):
    """Build the Champion's Hall (40×22) — central hub with 18 gym doors."""

    W, H = MAP_W, MAP_H
    g = [['.' for _ in range(W)] for _ in range(H)]

    # ── Perimeter walls ──
    for x in range(W):
        g[0][x] = '#'
        g[H - 1][x] = '#'
    for y in range(H):
        g[y][0] = '#'
        g[y][W - 1] = '#'

    # ── Red carpet runner (center, cols 18-21) ──
    for y in range(1, H - 1):
        for x in range(18, 22):
            g[y][x] = 'c'

    # ── Throne at top ──
    for x in range(16, 24):
        g[1][x] = 'T'
        g[2][x] = 'T'
    g[1][19] = 'K'
    g[1][20] = 'K'

    # ── Top wall decorations ──
    g[0][6]  = 'V'
    g[0][13] = 'W'
    g[0][20] = 'V'
    g[0][26] = 'W'
    g[0][33] = 'V'

    # ── Pillars flanking carpet ──
    for y in [4, 7, 10, 13, 16, 19]:
        if y < H - 1:
            g[y][16] = 'P'
            g[y][23] = 'P'

    # ── Wall torches ──
    for y in [3, 8, 13, 18]:
        if y < H - 1:
            g[y][1] = 'X'
            g[y][W - 2] = 'X'

    # ── Trophies ──
    g[3][15] = 'Y'
    g[3][24] = 'Y'
    g[2][3]  = 'Y'
    g[2][36] = 'Y'

    # ── Pokeball displays ──
    g[1][5]  = 'O'
    g[1][34] = 'O'

    # ── Bookshelves ──
    g[1][3]  = 'B'
    g[1][36] = 'B'

    # ── League sign ──
    g[0][37] = 'N'

    # ── Now place the 18 gym doors ──
    # Left wall: 9 doors (y= 2,4,6,8,10,12,14,16,18)
    # Right wall: 9 doors
    door_positions_left = []
    door_positions_right = []
    for i in range(9):
        dy = 2 + i * 2
        if dy < H - 1:
            door_positions_left.append((2, dy))
            door_positions_right.append((W - 3, dy))

    all_door_pos = door_positions_left + door_positions_right
    doors = {}
    door_tiles = {}
    door_labels = {}

    league = league_members or []
    members = league[:-1] if league else []  # all except champion (player)

    for i, pos in enumerate(all_door_pos):
        if i >= len(members):
            break
        member = members[i]
        specialty = member.specialty or "Normal"
        accent = TYPE_COLORS.get(specialty, (148, 152, 162))
        dx, dy = pos
        g[dy][dx] = '.'  # walkable floor under door
        is_current = (i == challenger_position)
        doors[(dx, dy)] = member.name
        door_tiles[(dx, dy)] = _make_door_tile(accent, is_current)
        door_labels[(dx, dy)] = member

    tile_data = [''.join(row) for row in g]

    ts = ThemedTileSet(accent=C_CARPET, seed=42)

    npcs = []
    npcs.append(NPC(
        28, H - 3, "Guide", 'up',
        "Welcome, Champion!\n"
        "Use ARROW KEYS to move.\n"
        "Press SPACE to interact.\n"
        "Step on a colored DOOR to enter a Gym!",
        None, 'guide'
    ))

    game_map = GameMap(tile_data, npcs, roaming=[], name="Champion's Hall",
                       tileset=ts, doors=doors)
    game_map._door_tiles = door_tiles
    game_map._door_labels = door_labels
    return game_map


# ═══════════════════════════════════════════════════════════════════
#  Gym Room Builder
# ═══════════════════════════════════════════════════════════════════

def build_gym(member, league_idx, challenger_position):
    """Build a type-themed gym room for a league member (40×22).

    Args:
        member: Trainer object (the gym leader / elite member)
        league_idx: position in the league list (0-based)
        challenger_position: current challenger_position from GameState
    """
    W, H = MAP_W, MAP_H
    specialty = member.specialty or "Normal"
    accent = TYPE_COLORS.get(specialty, (148, 152, 162))
    rng = random.Random(hash(member.name))

    g = [['.' for _ in range(W)] for _ in range(H)]

    # ── Perimeter walls ──
    for x in range(W):
        g[0][x] = '#'
        g[H - 1][x] = '#'
    for y in range(H):
        g[y][0] = '#'
        g[y][W - 1] = '#'

    # ── Wall decorations ──
    g[0][10] = 'V'
    g[0][20] = 'V'
    g[0][29] = 'V'
    g[0][6]  = 'W'
    g[0][15] = 'W'
    g[0][24] = 'W'
    g[0][33] = 'W'

    # ── Torches ──
    for y in [3, 8, 13, 18]:
        if y < H - 1:
            g[y][1] = 'X'
            g[y][W - 2] = 'X'

    # ── Carpet to leader ──
    for y in range(H - 3, 4, -1):
        for x in range(18, 22):
            g[y][x] = 'c'

    # ── Leader podium ──
    for x in range(17, 23):
        g[3][x] = 'T'
        g[4][x] = 'T'

    # ── Pillars ──
    for y in [3, 7, 11, 15, 19]:
        if y < H - 1:
            g[y][5] = 'P'
            g[y][34] = 'P'

    # ── Type decorations ──
    # Liquids for applicable types
    liquid_types = {"Fire", "Water", "Ice", "Poison", "Dragon", "Ghost"}
    if specialty in liquid_types:
        pool_spots = [(3, 6), (4, 6), (3, 7), (4, 7),
                      (35, 6), (36, 6), (35, 7), (36, 7),
                      (3, 14), (4, 14), (3, 15), (4, 15),
                      (35, 14), (36, 14), (35, 15), (36, 15)]
        for px, py in pool_spots:
            if 1 <= px < W - 1 and 1 <= py < H - 1:
                g[py][px] = '~'

    # Scattered floor decorations
    for _ in range(14):
        fx = rng.randint(3, W - 4)
        fy = rng.randint(5, H - 4)
        if g[fy][fx] == '.' and not (17 <= fx <= 22):
            g[fy][fx] = 'f'

    # ── Exit door at bottom center ──
    exit_x1, exit_x2 = 19, 20
    exit_y = H - 1
    g[exit_y][exit_x1] = '.'
    g[exit_y][exit_x2] = '.'
    doors = {
        (exit_x1, exit_y): "champion_room",
        (exit_x2, exit_y): "champion_room",
    }

    tile_data = [''.join(row) for row in g]

    ts = ThemedTileSet(accent=accent, seed=hash(member.name) % 10000)

    # ── Leader NPC ──
    npcs = [
        NPC(19, 5, member.name, 'down',
            "",  # dialogue handled dynamically by overworld
            member.name, 'gym_leader')
    ]

    # ── Roaming Pokemon ──
    roaming = []
    occupied = {(19, 5)}
    for poke in member.team:
        for _ in range(50):
            rx = rng.randint(3, W - 4)
            ry = rng.randint(6, H - 3)
            if g[ry][rx] in ('.', 'c', 'f') and (rx, ry) not in occupied:
                roaming.append(RoamingPokemon(poke.species, rx, ry))
                occupied.add((rx, ry))
                break

    game_map = GameMap(tile_data, npcs, roaming, name=f"{member.name}'s Gym",
                       tileset=ts, doors=doors)
    game_map.gym_leader = member
    game_map.league_idx = league_idx
    game_map.is_battle_gym = (league_idx == challenger_position)

    # Build exit door tile (stone floor with arrow)
    exit_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    exit_tile.fill(C_STONE)
    pygame.draw.rect(exit_tile, C_STONE_LINE, (0, 0, TILE_SIZE, TILE_SIZE), 1)
    cx, cy = TILE_SIZE // 2, TILE_SIZE // 2
    pts = [(cx, cy + 10), (cx - 8, cy - 2), (cx + 8, cy - 2)]
    pygame.draw.polygon(exit_tile, C_CARPET_GOLD, pts)
    game_map._door_tiles[(exit_x1, exit_y)] = exit_tile
    game_map._door_tiles[(exit_x2, exit_y)] = exit_tile.copy()

    return game_map
