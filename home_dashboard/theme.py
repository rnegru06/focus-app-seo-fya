"""Linear Frost design tokens — colors, spacing, fonts."""
from pathlib import Path
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

# Single bundled TTF — same file used for both proportional and mono callers.
_FONT_PATH = str(Path(__file__).resolve().parent / "assets" / "fonts" / "main.ttf")

_cache: dict[tuple, pygame.font.Font] = {}


def font(size: int, weight: str = "regular") -> pygame.font.Font:
    """Proportional font at the given size. weight='bold' applies bold."""
    key = ("sans", size, weight)
    if key in _cache:
        return _cache[key]
    f = pygame.font.Font(_FONT_PATH, size)
    if weight == "bold":
        f.set_bold(True)
    _cache[key] = f
    return f


def mono_font(size: int, weight: str = "regular") -> pygame.font.Font:
    """We only ship one TTF, so the countdown clock reuses the main font.
    Most modern UI fonts have tabular figures, so digit width stays stable
    enough for an mm:ss countdown."""
    key = ("mono", size, weight)
    if key in _cache:
        return _cache[key]
    f = pygame.font.Font(_FONT_PATH, size)
    if weight == "bold":
        f.set_bold(True)
    _cache[key] = f
    return f
