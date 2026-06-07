"""TimerScreen — runs the focus/break cycle. Pause toggles, Stop returns home.
Completed focus phases are recorded; in-progress phases are not.

Visual: a big progress ring fills clockwise as the phase progresses, with
the mm:ss countdown inside. The ring is accent purple during focus and a
calmer blue during break. A "Play Snake" button appears during break and
transitions to the embedded snake mini-game screen."""
import pygame

import theme
import audio
from widgets import Button, IconButton, ProgressRing
from data import stats

WINDOW_W, WINDOW_H = 1000, 700

PHASE_FOCUS = "focus"
PHASE_BREAK = "break"

# Calmer blue for break phase — visually distinct from focus accent.
BREAK_COLOR = (94, 150, 210)


class TimerScreen:
    def __init__(
        self,
        focus_minutes: int,
        break_minutes: int,
        custom_focus: int = 25,
        custom_break: int = 5,
        selected_cycle: str = "25/5",
    ):
        # --- cycle settings + state ---
        self.focus_minutes = max(1, int(focus_minutes))
        self.break_minutes = max(0, int(break_minutes))
        self._custom_focus = custom_focus
        self._custom_break = custom_break
        self._selected_cycle = selected_cycle

        self.phase = PHASE_FOCUS
        self.time_left = float(self.focus_minutes * 60)
        # Snapshot of the phase's total length so the progress ring can
        # compute (1 - time_left / total). Snapshotting at phase entry
        # protects against mid-phase setting changes.
        self._phase_total = self.time_left
        self.paused = False
        self._next_screen = None

        # --- widgets ---
        center_x = WINDOW_W // 2

        self.back_btn = IconButton(
            pygame.Rect(18, 18, 36, 36),
            glyph="←",
            on_click=self._on_back,
        )

        # Big progress ring as the time-passing visual.
        self.ring = ProgressRing(center=(center_x, 300), radius=150, ring_width=12)
        self.ring.color = theme.ACCENT  # focus by default

        btn_w, btn_h, gap = 140, 52, 16
        total_w = btn_w * 2 + gap
        left_x = center_x - total_w // 2
        self.pause_btn = Button(
            pygame.Rect(left_x, 540, btn_w, btn_h),
            label="Pause",
            on_click=self._on_pause,
            kind="primary",
        )
        self.stop_btn = Button(
            pygame.Rect(left_x + btn_w + gap, 540, btn_w, btn_h),
            label="Stop",
            on_click=self._on_stop,
            kind="ghost",
        )

        # Play Snake button — only handled / drawn during break.
        snake_w, snake_h = 200, 40
        self.snake_btn = Button(
            pygame.Rect(center_x - snake_w // 2, 615, snake_w, snake_h),
            label="🐍  Play Snake",
            on_click=self._on_play_snake,
            kind="ghost",
        )

    # --- event handlers ---

    def _on_back(self) -> None:
        self._return_home()

    def _on_pause(self) -> None:
        self.paused = not self.paused
        self.pause_btn.label = "Resume" if self.paused else "Pause"
        # Mirror in audio so music pauses with the timer.
        if self.paused:
            audio.pause()
        else:
            audio.resume()

    def _on_stop(self) -> None:
        self._return_home()

    def _on_play_snake(self) -> None:
        # Transition to the embedded snake screen, handing it the break
        # cycle settings + the remaining break time so it can auto-close
        # when the break clock hits 0.
        from screens.break_game import BreakGameScreen
        # Resume music in case the user paused; the snake screen owns its
        # own UX from here.
        audio.resume()
        self.paused = False
        self.pause_btn.label = "Pause"
        self._next_screen = BreakGameScreen(
            focus_minutes=self.focus_minutes,
            break_minutes=self.break_minutes,
            time_left_seconds=self.time_left,
            custom_focus=self._custom_focus,
            custom_break=self._custom_break,
            selected_cycle=self._selected_cycle,
            standalone=False,
        )

    def _return_home(self) -> None:
        # Resume music in case it was paused — home screen expects it playing.
        audio.resume()
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
        # Play the chime to mark every phase transition.
        audio.play_chime()
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
        # Reset phase-total snapshot for the new phase.
        self._phase_total = self.time_left
        # Re-color the ring for the new phase.
        self.ring.color = theme.ACCENT if self.phase == PHASE_FOCUS else BREAK_COLOR

    # --- screen API ---

    def handle_event(self, event: pygame.event.Event):
        self.back_btn.handle_event(event)
        self.pause_btn.handle_event(event)
        self.stop_btn.handle_event(event)
        # Snake button only listens during break.
        if self.phase == PHASE_BREAK:
            self.snake_btn.handle_event(event)
        nxt = self._next_screen
        self._next_screen = None
        return nxt

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self._advance_phase()

        # Update the ring's progress fraction (clamped to a clean 0..1).
        if self._phase_total > 0:
            self.ring.progress = max(0.0, min(1.0, 1.0 - self.time_left / self._phase_total))

    def draw(self, surface: pygame.Surface) -> None:
        self.back_btn.draw(surface)

        # Big progress ring (drawn first; text overlays on top).
        self.ring.draw(surface)

        # Countdown inside the ring — mono font for stable digit width.
        total = max(0, int(self.time_left + 0.5))
        m, s = divmod(total, 60)
        time_text = f"{m:02d}:{s:02d}" if m < 100 else f"{m}:{s:02d}"
        time_surf = theme.mono_font(64, "bold").render(time_text, True, theme.TEXT)
        surface.blit(time_surf, time_surf.get_rect(center=self.ring.center))

        # Phase label below the ring.
        if self.phase == PHASE_FOCUS:
            phase_text, phase_color = "FOCUS", theme.ACCENT
        else:
            phase_text, phase_color = "BREAK", BREAK_COLOR
        phase_surf = theme.font(14, "bold").render(phase_text, True, phase_color)
        surface.blit(phase_surf, phase_surf.get_rect(center=(WINDOW_W // 2, 482)))

        # Cycle setting line — even smaller, muted.
        sub = f"{self.focus_minutes} min focus · {self.break_minutes} min break"
        sub_surf = theme.font(13, "regular").render(sub, True, theme.TEXT_MUTED)
        surface.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_W // 2, 505)))

        # Paused indicator overlays the bottom of the ring.
        if self.paused:
            paused_surf = theme.font(13, "bold").render("PAUSED", True, theme.TEXT_MUTED)
            surface.blit(paused_surf, paused_surf.get_rect(
                center=(self.ring.center[0], self.ring.center[1] + 90)
            ))

        self.pause_btn.draw(surface)
        self.stop_btn.draw(surface)

        # Play Snake button only during break.
        if self.phase == PHASE_BREAK:
            self.snake_btn.draw(surface)
