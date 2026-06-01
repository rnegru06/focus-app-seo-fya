"""Linear Frost design tokens — colors, spacing, fonts."""
import pygame

BG           = (8, 9, 10)
SURFACE      = (28, 29, 32)
SURFACE_2    = (38, 39, 43)
TEXT         = (244, 244, 245)
TEXT_MUTED   = (142, 142, 147)
ACCENT       = (94, 106, 210)
ACCENT_HOVER = (123, 133, 220)

SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL = 4, 8, 16, 24, 40

RADIUS_SM, RADIUS_MD, RADIUS_LG = 6, 10, 16

_FONT_CANDIDATES = {
    "regular": ["Inter", "SF Pro Text", "Helvetica Neue", "Helvetica", "Arial"],
    "bold":    ["Inter", "SF Pro Text", "Helvetica Neue", "Helvetica", "Arial"],
}

_MONO_CANDIDATES = ["SF Mono", "Menlo", "Monaco", "Consolas", "Courier New", "Courier"]

_cache: dict[tuple, pygame.font.Font] = {}


def font(size: int, weight: str = "regular") -> pygame.font.Font:
    key = ("sans", size, weight)
    if key in _cache:
        return _cache[key]
    bold = weight == "bold"
    chosen = pygame.font.match_font(",".join(_FONT_CANDIDATES[weight]), bold=bold)
    f = pygame.font.Font(chosen, size) if chosen else pygame.font.Font(None, size)
    if bold and not chosen:
        f.set_bold(True)
    _cache[key] = f
    return f


def mono_font(size: int, weight: str = "regular") -> pygame.font.Font:
    key = ("mono", size, weight)
    if key in _cache:
        return _cache[key]
    bold = weight == "bold"
    chosen = pygame.font.match_font(",".join(_MONO_CANDIDATES), bold=bold)
    f = pygame.font.Font(chosen, size) if chosen else pygame.font.Font(None, size)
    if bold and not chosen:
        f.set_bold(True)
    _cache[key] = f
    return f
