"""Reusable UI primitives. Each widget owns a rect, draws itself,
and reports whether it consumed a click via handle_event()."""
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
