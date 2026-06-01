"""SettingsScreen — back button, reset-today action, placeholder for future options."""
import pygame

import theme
from widgets import Button, IconButton, Card
from data import stats

WINDOW_W, WINDOW_H = 1000, 700


class SettingsScreen:
    def __init__(self):
        self._next_screen = None
        self._reset_confirmed = False

        self.back_btn = IconButton(
            pygame.Rect(18, 18, 36, 36),
            glyph="←",
            on_click=self._on_back,
        )

        center_x = WINDOW_W // 2
        card_w, card_h = 720, 88
        self.card = Card(pygame.Rect(center_x - card_w // 2, 180, card_w, card_h))

        btn_w, btn_h = 160, 40
        self.reset_btn = Button(
            pygame.Rect(self.card.rect.right - theme.SPACE_LG - btn_w,
                        self.card.rect.y + (card_h - btn_h) // 2,
                        btn_w, btn_h),
            label="Reset",
            on_click=self._on_reset,
            kind="ghost",
        )

    def _on_back(self) -> None:
        from screens.home import HomeScreen
        self._next_screen = HomeScreen()

    def _on_reset(self) -> None:
        stats.reset_today()
        self._reset_confirmed = True

    def handle_event(self, event: pygame.event.Event):
        self.back_btn.handle_event(event)
        self.reset_btn.handle_event(event)
        nxt = self._next_screen
        self._next_screen = None
        return nxt

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        self.back_btn.draw(surface)

        title = theme.font(22, "bold").render("Settings", True, theme.TEXT)
        surface.blit(title, title.get_rect(center=(WINDOW_W // 2, 38)))

        # Reset card
        self.card.draw(surface)
        rect = self.card.rect
        label = theme.font(16, "bold").render("Reset today's stats", True, theme.TEXT)
        sub_text = ("Today's count cleared."
                    if self._reset_confirmed
                    else "Clears today's session count and total minutes.")
        sub = theme.font(13, "regular").render(sub_text, True, theme.TEXT_MUTED)
        surface.blit(label, (rect.x + theme.SPACE_LG, rect.y + theme.SPACE_LG))
        surface.blit(sub, (rect.x + theme.SPACE_LG,
                           rect.y + theme.SPACE_LG + label.get_height() + 4))
        self.reset_btn.draw(surface)

        # Placeholder for future settings
        note = theme.font(13, "regular").render(
            "More options coming soon — themes, music, history.",
            True, theme.TEXT_MUTED,
        )
        surface.blit(note, note.get_rect(center=(WINDOW_W // 2, WINDOW_H - 48)))
