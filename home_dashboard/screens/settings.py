"""SettingsScreen — back button, music picker, volume slider, reset-today action.
All choices persist to preferences.json so they survive across launches."""
import pygame

import theme
import audio
from widgets import Button, Chip, IconButton, Card, Slider
from data import stats, preferences

WINDOW_W, WINDOW_H = 1000, 700

# Display labels for each music track (and "off"). Display order matches the
# chip row left-to-right.
TRACK_OPTIONS = [
    ("Off",         "off"),
    ("Rain",        "rain"),
    ("Forest",      "forest"),
    ("White Noise", "white_noise"),
]


class SettingsScreen:
    def __init__(self):
        self._next_screen = None
        self._reset_confirmed = False
        prefs = preferences.load()
        self._current_track = prefs["music_track"]

        # --- Back arrow ---
        self.back_btn = IconButton(
            pygame.Rect(18, 18, 36, 36),
            glyph="←",
            on_click=self._on_back,
        )

        center_x = WINDOW_W // 2

        # --- Music card with chips + slider ---
        music_card_w, music_card_h = 720, 180
        self.music_card = Card(
            pygame.Rect(center_x - music_card_w // 2, 100, music_card_w, music_card_h)
        )

        # Chip row inside the music card.
        chip_w, chip_h, gap = 130, 36, 12
        total_w = chip_w * len(TRACK_OPTIONS) + gap * (len(TRACK_OPTIONS) - 1)
        chips_start_x = center_x - total_w // 2
        chips_y = self.music_card.rect.y + 60
        self.music_chips: list[Chip] = []
        for i, (label, value) in enumerate(TRACK_OPTIONS):
            rect = pygame.Rect(chips_start_x + i * (chip_w + gap), chips_y, chip_w, chip_h)
            chip = Chip(rect, label, value, self._on_track_chip)
            chip.selected = (value == self._current_track)
            self.music_chips.append(chip)

        # Volume slider centered below the chips.
        slider_w = 480
        self.volume_slider = Slider(
            pygame.Rect(center_x - slider_w // 2, self.music_card.rect.y + 130, slider_w, 24),
            value=prefs["volume"],
            on_change=self._on_volume_change,
            on_release=self._on_volume_release,
        )

        # --- Reset stats card ---
        reset_card_h = 88
        self.reset_card = Card(
            pygame.Rect(center_x - 720 // 2, 310, 720, reset_card_h)
        )
        btn_w, btn_h = 160, 40
        self.reset_btn = Button(
            pygame.Rect(self.reset_card.rect.right - theme.SPACE_LG - btn_w,
                        self.reset_card.rect.y + (reset_card_h - btn_h) // 2,
                        btn_w, btn_h),
            label="Reset",
            on_click=self._on_reset,
            kind="ghost",
        )

    # --- event handlers ---

    def _on_back(self) -> None:
        from screens.home import HomeScreen
        self._next_screen = HomeScreen()

    def _on_reset(self) -> None:
        stats.reset_today()
        self._reset_confirmed = True

    def _on_track_chip(self, value: str) -> None:
        # Update selection visuals, switch audio, persist.
        self._current_track = value
        for chip in self.music_chips:
            chip.selected = chip.value == value
        audio.play(value)
        prefs = preferences.load()
        prefs["music_track"] = value
        preferences.save(prefs)

    def _on_volume_change(self, v: float) -> None:
        # Live-apply volume while dragging — feels responsive.
        audio.set_volume(v)

    def _on_volume_release(self, v: float) -> None:
        # Only persist on mouse-up so we don't spam writes during the drag.
        prefs = preferences.load()
        prefs["volume"] = v
        preferences.save(prefs)

    # --- screen API ---

    def handle_event(self, event: pygame.event.Event):
        self.back_btn.handle_event(event)
        for chip in self.music_chips:
            chip.handle_event(event)
        self.volume_slider.handle_event(event)
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

        # --- Music card ---
        self.music_card.draw(surface)
        music_rect = self.music_card.rect
        label = theme.font(16, "bold").render("Background music", True, theme.TEXT)
        sub = theme.font(13, "regular").render(
            "Pick an ambient track and adjust the volume.",
            True, theme.TEXT_MUTED,
        )
        surface.blit(label, (music_rect.x + theme.SPACE_LG, music_rect.y + theme.SPACE_MD))
        surface.blit(sub, (music_rect.x + theme.SPACE_LG,
                           music_rect.y + theme.SPACE_MD + label.get_height() + 2))
        for chip in self.music_chips:
            chip.draw(surface)
        self.volume_slider.draw(surface)
        # Volume % readout to the right of the slider.
        vol_pct = int(round(self.volume_slider.value * 100))
        vol_text = theme.font(13, "regular").render(f"{vol_pct}%", True, theme.TEXT_MUTED)
        surface.blit(vol_text, vol_text.get_rect(
            midleft=(self.volume_slider.rect.right + theme.SPACE_MD,
                     self.volume_slider.rect.centery),
        ))

        # --- Reset stats card ---
        self.reset_card.draw(surface)
        rect = self.reset_card.rect
        rlabel = theme.font(16, "bold").render("Reset today's stats", True, theme.TEXT)
        sub_text = ("Today's count cleared."
                    if self._reset_confirmed
                    else "Clears today's session count and total minutes.")
        rsub = theme.font(13, "regular").render(sub_text, True, theme.TEXT_MUTED)
        surface.blit(rlabel, (rect.x + theme.SPACE_LG, rect.y + theme.SPACE_LG))
        surface.blit(rsub, (rect.x + theme.SPACE_LG,
                            rect.y + theme.SPACE_LG + rlabel.get_height() + 4))
        self.reset_btn.draw(surface)

        # --- Footer note ---
        note = theme.font(13, "regular").render(
            "More options coming soon — themes and history.",
            True, theme.TEXT_MUTED,
        )
        surface.blit(note, note.get_rect(center=(WINDOW_W // 2, WINDOW_H - 48)))
