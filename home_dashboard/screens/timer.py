"""TimerScreen — runs the focus/break cycle. Pause toggles, Stop returns home.
Completed focus phases are recorded; in-progress phases are not."""
import pygame

import theme
from widgets import Button, IconButton
from data import stats

WINDOW_W, WINDOW_H = 1000, 700

PHASE_FOCUS = "focus"
PHASE_BREAK = "break"


class TimerScreen:
    def __init__(
        self,
        focus_minutes: int,
        break_minutes: int,
        custom_focus: int = 25,
        custom_break: int = 5,
        selected_cycle: str = "25/5",
    ):
        self.focus_minutes = max(1, int(focus_minutes))
        self.break_minutes = max(0, int(break_minutes))
        self._custom_focus = custom_focus
        self._custom_break = custom_break
        self._selected_cycle = selected_cycle

        self.phase = PHASE_FOCUS
        self.time_left = float(self.focus_minutes * 60)
        self.paused = False
        self._next_screen = None

        center_x = WINDOW_W // 2

        self.back_btn = IconButton(
            pygame.Rect(18, 18, 36, 36),
            glyph="←",
            on_click=self._on_back,
        )

        btn_w, btn_h, gap = 140, 52, 16
        total_w = btn_w * 2 + gap
        left_x = center_x - total_w // 2
        self.pause_btn = Button(
            pygame.Rect(left_x, 490, btn_w, btn_h),
            label="Pause",
            on_click=self._on_pause,
            kind="primary",
        )
        self.stop_btn = Button(
            pygame.Rect(left_x + btn_w + gap, 490, btn_w, btn_h),
            label="Stop",
            on_click=self._on_stop,
            kind="ghost",
        )

    # --- event handlers ---

    def _on_back(self) -> None:
        self._return_home()

    def _on_pause(self) -> None:
        self.paused = not self.paused
        self.pause_btn.label = "Resume" if self.paused else "Pause"

    def _on_stop(self) -> None:
        self._return_home()

    def _return_home(self) -> None:
        from screens.home import HomeScreen
        self._next_screen = HomeScreen(
            custom_focus=self._custom_focus,
            custom_break=self._custom_break,
        )
        # Restore the user's previously chosen cycle so they don't have to
        # re-pick it when coming back.
        self._next_screen.selected_cycle = self._selected_cycle
        for chip in self._next_screen.chips:
            chip.selected = chip.value == self._selected_cycle

    def _advance_phase(self) -> None:
        if self.phase == PHASE_FOCUS:
            stats.record_session(self.focus_minutes)
            if self.break_minutes > 0:
                self.phase = PHASE_BREAK
                self.time_left = float(self.break_minutes * 60)
            else:
                # zero-length break: stay in focus, reset clock
                self.time_left = float(self.focus_minutes * 60)
        else:
            self.phase = PHASE_FOCUS
            self.time_left = float(self.focus_minutes * 60)

    # --- screen API ---

    def handle_event(self, event: pygame.event.Event):
        self.back_btn.handle_event(event)
        self.pause_btn.handle_event(event)
        self.stop_btn.handle_event(event)
        nxt = self._next_screen
        self._next_screen = None
        return nxt

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._advance_phase()

    def draw(self, surface: pygame.Surface) -> None:
        self.back_btn.draw(surface)

        # Phase label — accent during focus, muted during break
        if self.phase == PHASE_FOCUS:
            phase_text = "FOCUS"
            phase_color = theme.ACCENT
        else:
            phase_text = "BREAK"
            phase_color = theme.TEXT_MUTED
        phase_surf = theme.font(14, "bold").render(phase_text, True, phase_color)
        surface.blit(phase_surf, phase_surf.get_rect(center=(WINDOW_W // 2, 220)))

        # Countdown — big mono font, mm:ss
        total = max(0, int(self.time_left + 0.5))
        m, s = divmod(total, 60)
        # cap minutes display at 999 just to be safe with very long custom cycles
        time_text = f"{m:02d}:{s:02d}" if m < 100 else f"{m}:{s:02d}"
        time_surf = theme.mono_font(110, "bold").render(time_text, True, theme.TEXT)
        surface.blit(time_surf, time_surf.get_rect(center=(WINDOW_W // 2, 340)))

        # Cycle setting line under the clock
        sub = f"{self.focus_minutes} min focus · {self.break_minutes} min break"
        sub_surf = theme.font(14, "regular").render(sub, True, theme.TEXT_MUTED)
        surface.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_W // 2, 420)))

        # Paused indicator
        if self.paused:
            paused_surf = theme.font(13, "bold").render("PAUSED", True, theme.TEXT_MUTED)
            surface.blit(paused_surf, paused_surf.get_rect(center=(WINDOW_W // 2, 450)))

        self.pause_btn.draw(surface)
        self.stop_btn.draw(surface)
