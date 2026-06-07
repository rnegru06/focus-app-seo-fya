"""Reusable UI primitives. Each widget owns a rect, draws itself,
and reports whether it consumed a click via handle_event()."""
import math
from typing import Callable, Optional
import pygame

import theme


class Widget:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class Button(Widget):
    """Filled rectangle CTA. Use kind='primary' for accent fill, 'ghost' for outline."""

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        on_click: Callable[[], None],
        kind: str = "primary",
    ):
        super().__init__(rect)
        self.label = label
        self.on_click = on_click
        self.kind = kind

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if self.kind == "primary":
            color = theme.ACCENT_HOVER if self.hovered else theme.ACCENT
            pygame.draw.rect(surface, color, self.rect, border_radius=theme.RADIUS_MD)
        else:
            pygame.draw.rect(surface, theme.SURFACE, self.rect, border_radius=theme.RADIUS_MD)
            pygame.draw.rect(surface, theme.SURFACE_2, self.rect, width=1, border_radius=theme.RADIUS_MD)
        text_surf = theme.font(18, "bold").render(self.label, True, theme.TEXT)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class Chip(Widget):
    """Pill-shaped toggle. Selected chips fill with accent; others are outlined."""

    def __init__(self, rect: pygame.Rect, label: str, value: str, on_click: Callable[[str], None]):
        super().__init__(rect)
        self.label = label
        self.value = value
        self.on_click = on_click
        self.selected = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click(self.value)
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        radius = self.rect.height // 2
        if self.selected:
            pygame.draw.rect(surface, theme.ACCENT, self.rect, border_radius=radius)
            text_color = theme.TEXT
        else:
            fill = theme.SURFACE if self.hovered else theme.BG
            pygame.draw.rect(surface, fill, self.rect, border_radius=radius)
            pygame.draw.rect(surface, theme.SURFACE_2, self.rect, width=1, border_radius=radius)
            text_color = theme.TEXT_MUTED if not self.hovered else theme.TEXT
        text_surf = theme.font(15, "regular").render(self.label, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class IconButton(Widget):
    """Small circular button rendering a single glyph (e.g., gear ⚙)."""

    def __init__(self, rect: pygame.Rect, glyph: str, on_click: Callable[[], None]):
        super().__init__(rect)
        self.glyph = glyph
        self.on_click = on_click

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if self.hovered:
            pygame.draw.rect(surface, theme.SURFACE, self.rect, border_radius=theme.RADIUS_MD)
        glyph_surf = theme.font(20, "regular").render(self.glyph, True, theme.TEXT_MUTED if not self.hovered else theme.TEXT)
        surface.blit(glyph_surf, glyph_surf.get_rect(center=self.rect.center))


class Card(Widget):
    """Rounded container with subtle border. Holds content drawn by the screen."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, theme.SURFACE, self.rect, border_radius=theme.RADIUS_LG)
        pygame.draw.rect(surface, theme.SURFACE_2, self.rect, width=1, border_radius=theme.RADIUS_LG)


class NumberInput(Widget):
    """Numeric text input. Click to focus, type digits, backspace to delete.
    Clicking elsewhere blurs. Enter/Esc also blur."""

    def __init__(
        self,
        rect: pygame.Rect,
        value: int = 0,
        max_digits: int = 3,
        on_change: Optional[Callable[[int], None]] = None,
    ):
        super().__init__(rect)
        self._text = str(value) if value > 0 else ""
        self.max_digits = max_digits
        self.active = False
        self.on_change = on_change

    @property
    def value(self) -> int:
        return int(self._text) if self._text else 0

    @value.setter
    def value(self, v: int) -> None:
        self._text = str(v) if v > 0 else ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inside = self.rect.collidepoint(event.pos)
            if inside:
                self.active = True
                return True
            if self.active:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self._text:
                    self._text = self._text[:-1]
                    if self.on_change:
                        self.on_change(self.value)
                return True
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_TAB):
                self.active = False
                return True
            if event.unicode.isdigit() and len(self._text) < self.max_digits:
                # disallow leading zeros (so "0" doesn't pad to "025")
                if self._text == "0":
                    self._text = event.unicode
                else:
                    self._text += event.unicode
                if self.on_change:
                    self.on_change(self.value)
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, theme.SURFACE, self.rect, border_radius=theme.RADIUS_MD)
        border_color = theme.ACCENT if self.active else theme.SURFACE_2
        border_width = 2 if self.active else 1
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=theme.RADIUS_MD)

        display = self._text if self._text else "—"
        color = theme.TEXT if self._text else theme.TEXT_MUTED
        text_surf = theme.font(18, "bold").render(display, True, color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class ProgressRing(Widget):
    """Clockwise-filling ring. Set .progress in [0..1] each frame; the arc
    grows from 12 o'clock. Drawn as a filled "pie slice" polygon clipped
    by a smaller background-colored disk on top — avoids pygame.draw.arc's
    flaky thick-line rendering. Content (e.g., countdown text) is drawn by
    the screen separately, layered inside this ring."""

    def __init__(self, center: tuple[int, int], radius: int, ring_width: int = 10):
        rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        super().__init__(rect)
        self.center = center
        self.radius = radius
        self.ring_width = ring_width
        self.progress = 0.0           # 0..1
        self.color = theme.ACCENT
        self.bg_color = theme.BG      # used to "punch out" the inner disk

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = self.center
        r_outer = self.radius
        r_inner = self.radius - self.ring_width

        # Faint background ring — always visible as a track outline.
        pygame.draw.circle(surface, theme.SURFACE_2, self.center, r_outer, width=1)

        progress = max(0.0, min(1.0, self.progress))

        # Build a polygon "pie slice": center + arc points from 12 o'clock
        # going clockwise by (progress * 2π). pygame angles are CCW with 0
        # at the east axis, so 12 o'clock = π/2 and clockwise means we
        # subtract from that.
        if progress > 0:
            n_segments = max(2, int(progress * 80))  # smooth at any size
            start_angle = math.pi / 2
            sweep = 2 * math.pi * progress
            points = [self.center]
            for i in range(n_segments + 1):
                a = start_angle - sweep * (i / n_segments)
                points.append((
                    cx + math.cos(a) * r_outer,
                    cy - math.sin(a) * r_outer,   # pygame y-axis is flipped
                ))
            if progress >= 0.999:
                pygame.draw.circle(surface, self.color, self.center, r_outer)
            else:
                pygame.draw.polygon(surface, self.color, points)

        # Punch out the center — leaves only the ring of ring_width thickness.
        pygame.draw.circle(surface, self.bg_color, self.center, r_inner)


class Slider(Widget):
    """Horizontal value picker in [0..1]. Click or drag to set. Accent fill
    on the left of the knob; subtle track on the right."""

    def __init__(
        self,
        rect: pygame.Rect,
        value: float = 0.5,
        on_change: Optional[Callable[[float], None]] = None,
        on_release: Optional[Callable[[float], None]] = None,
    ):
        super().__init__(rect)
        self.value = max(0.0, min(1.0, float(value)))
        self.on_change = on_change
        self.on_release = on_release        # fired only on mouse-up — for save throttling
        self._dragging = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        super().handle_event(event)
        # Expanded hit area — easier to grab on the knob.
        hit_rect = self.rect.inflate(0, 16)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hit_rect.collidepoint(event.pos):
                self._dragging = True
                self._set_from_x(event.pos[0])
                return True
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self._set_from_x(event.pos[0])
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._dragging:
            self._dragging = False
            if self.on_release:
                self.on_release(self.value)
            return True
        return False

    def _set_from_x(self, mouse_x: int) -> None:
        rel = (mouse_x - self.rect.x) / max(1, self.rect.width)
        new_value = max(0.0, min(1.0, rel))
        if new_value != self.value:
            self.value = new_value
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surface: pygame.Surface) -> None:
        # Track — full width, subtle.
        track_h = 8
        track_rect = pygame.Rect(
            self.rect.x, self.rect.centery - track_h // 2,
            self.rect.width, track_h,
        )
        pygame.draw.rect(surface, theme.SURFACE_2, track_rect, border_radius=track_h // 2)

        # Filled portion — accent up to the knob.
        fill_w = int(self.rect.width * self.value)
        if fill_w > 0:
            fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_w, track_h)
            pygame.draw.rect(surface, theme.ACCENT, fill_rect, border_radius=track_h // 2)

        # Knob — bigger when hovered/dragging for feedback.
        knob_x = self.rect.x + fill_w
        knob_r = 10 if (self.hovered or self._dragging) else 8
        pygame.draw.circle(surface, theme.TEXT, (knob_x, self.rect.centery), knob_r)
