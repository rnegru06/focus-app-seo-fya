"""Animated particle background — soft drifting glowing dots behind every
screen. Subtle enough not to distract during focus, alive enough that the
window never looks empty. Uses additive blending for the glow."""
import math
import random
from typing import Optional

import pygame

import theme


# --- particle data ---
# Tuned for a subtle moving haze — large soft washes that you can see but
# that never demand attention. Visible enough to feel alive, low enough
# alpha to stay out of the way of foreground text and UI.

NUM_PARTICLES = 20
MIN_RADIUS, MAX_RADIUS = 100, 200        # big soft halos = blur-wash look
MIN_SPEED, MAX_SPEED   = 2, 6            # slow drift
MIN_ALPHA, MAX_ALPHA   = 14, 26          # visible but muted at center


class _Particle:
    """One drifting glow. Position wraps around screen edges."""

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self._respawn(initial=True)

    def _respawn(self, initial: bool = False) -> None:
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h)
        # Slow drift — angle anywhere, magnitude small.
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(MIN_RADIUS, MAX_RADIUS)
        self.alpha = random.randint(MIN_ALPHA, MAX_ALPHA)
        # Very narrow hue range around the accent purple — keeps the wash
        # uniform-looking instead of resolving into individual dots.
        r, g, b = theme.ACCENT
        self.color = (
            max(0, min(255, r + random.randint(-8, 8))),
            max(0, min(255, g + random.randint(-8, 8))),
            max(0, min(255, b + random.randint(-8, 8))),
        )

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Wrap around edges so the field always feels full.
        if self.x < -self.radius:    self.x = self.w + self.radius
        if self.x > self.w + self.radius: self.x = -self.radius
        if self.y < -self.radius:    self.y = self.h + self.radius
        if self.y > self.h + self.radius: self.y = -self.radius


class ParticleBackground:
    """Drives ~28 particles. update(dt) ticks motion, draw(surface) blits
    a pre-rendered glow sprite per particle with BLEND_ADD."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._particles = [_Particle(width, height) for _ in range(NUM_PARTICLES)]
        # Pre-render a single radial-gradient glow sprite per (radius, color, alpha)
        # combination. We cache them so we don't redraw the gradient every frame.
        self._glow_cache: dict[tuple, pygame.Surface] = {}

    def update(self, dt: float) -> None:
        for p in self._particles:
            p.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        # Plain alpha blend (not additive) so colors stay muted and
        # overlapping particles don't brighten into saturated highlights.
        for p in self._particles:
            glow = self._glow(p.radius, p.color, p.alpha)
            rect = glow.get_rect(center=(int(p.x), int(p.y)))
            surface.blit(glow, rect)

    def _glow(self, radius: int, color: tuple, alpha: int) -> pygame.Surface:
        """Build (or fetch from cache) a radial-fade glow sprite — strongest
        in the very center, then a steep falloff so the edges are invisible.
        Result reads more like a soft blurred wash than a discrete dot."""
        key = (radius, color, alpha)
        cached = self._glow_cache.get(key)
        if cached is not None:
            return cached
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Many concentric rings = smooth gradient. Steep exponent (3.0)
        # means most of the alpha falls off close to the center, leaving a
        # large soft blur with almost-invisible edges.
        n_rings = 18
        for i in range(n_rings, 0, -1):
            t = i / n_rings
            r = int(radius * t)
            a = int(alpha * (1 - t) ** 2.0)
            if a <= 0:
                continue
            ring_color = (color[0], color[1], color[2], a)
            pygame.draw.circle(surf, ring_color, (radius, radius), r)
        self._glow_cache[key] = surf
        return surf
