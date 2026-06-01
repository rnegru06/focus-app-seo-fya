"""HomeScreen — landing dashboard. Picks a focus cycle, starts a session,
shows today's stats. Transitions to TimerScreen on Start, SettingsScreen on gear."""
from typing import Optional
import pygame

import theme
from widgets import Button, Chip, IconButton, Card, NumberInput
from data import stats

WINDOW_W, WINDOW_H = 1000, 700

CYCLES = [
    ("25 / 5", "25/5"),
    ("50 / 10", "50/10"),
    ("Custom", "custom"),
]


class HomeScreen:
    def __init__(self, custom_focus: int = 25, custom_break: int = 5):
        self.selected_cycle = "25/5"
        self.custom_focus = custom_focus
        self.custom_break = custom_break
        self.today = stats.load_today()
        self._next_screen = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        center_x = WINDOW_W // 2

        # Top bar — gear icon top-right
        self.settings_btn = IconButton(
            pygame.Rect(WINDOW_W - 24 - 36, 18, 36, 36),
            glyph="⚙",
            on_click=self._on_settings,
        )

        # Cycle picker chips
        chip_w, chip_h, gap = 100, 36, 12
        total_w = chip_w * len(CYCLES) + gap * (len(CYCLES) - 1)
        start_x = center_x - total_w // 2
        self.chips: list[Chip] = []
        for i, (label, value) in enumerate(CYCLES):
            rect = pygame.Rect(start_x + i * (chip_w + gap), 240, chip_w, chip_h)
            chip = Chip(rect, label, value, self._on_chip)
            chip.selected = value == self.selected_cycle
            self.chips.append(chip)

        # Custom inputs (focus + break) — only drawn when Custom selected,
        # but built always so click areas are valid.
        input_w, input_h = 70, 38
        # Layout: "Focus [ NN ] min     Break [ NN ] min" — centered as a group
        focus_label_w = theme.font(14, "regular").size("Focus")[0]
        break_label_w = theme.font(14, "regular").size("Break")[0]
        min_label_w   = theme.font(14, "regular").size("min")[0]
        group_gap = 32
        section_gap = theme.SPACE_SM
        section_w = focus_label_w + section_gap + input_w + section_gap + min_label_w
        total_inputs_w = section_w * 2 + group_gap
        inputs_left = center_x - total_inputs_w // 2

        focus_input_x = inputs_left + focus_label_w + section_gap
        break_section_x = inputs_left + section_w + group_gap
        break_input_x = break_section_x + break_label_w + section_gap

        self._inputs_y = 305
        self.focus_input = NumberInput(
            pygame.Rect(focus_input_x, self._inputs_y, input_w, input_h),
            value=self.custom_focus,
            max_digits=3,
            on_change=self._on_focus_change,
        )
        self.break_input = NumberInput(
            pygame.Rect(break_input_x, self._inputs_y, input_w, input_h),
            value=self.custom_break,
            max_digits=3,
            on_change=self._on_break_change,
        )
        # Cache positions for labels so we draw consistently
        self._focus_label_pos = (inputs_left, self._inputs_y + input_h // 2)
        self._focus_min_pos = (focus_input_x + input_w + section_gap, self._inputs_y + input_h // 2)
        self._break_label_pos = (break_section_x, self._inputs_y + input_h // 2)
        self._break_min_pos = (break_input_x + input_w + section_gap, self._inputs_y + input_h // 2)

        # Start Focus button
        btn_w, btn_h = 280, 56
        self.start_btn = Button(
            pygame.Rect(center_x - btn_w // 2, 390, btn_w, btn_h),
            label="Start Focus",
            on_click=self._on_start,
            kind="primary",
        )

        # Today stats card — bottom
        card_w, card_h = 720, 100
        self.stats_card = Card(
            pygame.Rect(center_x - card_w // 2, 540, card_w, card_h)
        )

    # --- event handlers ---

    def _on_chip(self, value: str) -> None:
        self.selected_cycle = value
        for chip in self.chips:
            chip.selected = chip.value == value
        if value != "custom":
            self.focus_input.active = False
            self.break_input.active = False

    def _on_focus_change(self, v: int) -> None:
        self.custom_focus = v

    def _on_break_change(self, v: int) -> None:
        self.custom_break = v

    def _selected_minutes(self) -> tuple[int, int]:
        if self.selected_cycle == "25/5":
            return (25, 5)
        if self.selected_cycle == "50/10":
            return (50, 10)
        return (self.custom_focus, self.custom_break)

    def _on_start(self) -> None:
        focus, brk = self._selected_minutes()
        if focus < 1:
            print("Cannot start: focus must be at least 1 minute")
            return
        from screens.timer import TimerScreen
        self._next_screen = TimerScreen(
            focus_minutes=focus,
            break_minutes=max(0, brk),
            custom_focus=self.custom_focus,
            custom_break=self.custom_break,
            selected_cycle=self.selected_cycle,
        )

    def _on_settings(self) -> None:
        from screens.settings import SettingsScreen
        self._next_screen = SettingsScreen()

    # --- screen API ---

    def handle_event(self, event: pygame.event.Event):
        self.settings_btn.handle_event(event)
        for chip in self.chips:
            chip.handle_event(event)
        # Inputs only receive events when Custom is selected, so clicks
        # elsewhere don't accidentally focus them.
        if self.selected_cycle == "custom":
            self.focus_input.handle_event(event)
            self.break_input.handle_event(event)
        self.start_btn.handle_event(event)
        nxt = self._next_screen
        self._next_screen = None
        return nxt

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = theme.font(22, "bold").render("Focus", True, theme.TEXT)
        surface.blit(title, (theme.SPACE_LG, 24))
        self.settings_btn.draw(surface)

        hero = theme.font(15, "regular").render("Choose your cycle", True, theme.TEXT_MUTED)
        surface.blit(hero, hero.get_rect(center=(WINDOW_W // 2, 200)))

        for chip in self.chips:
            chip.draw(surface)

        if self.selected_cycle == "custom":
            self._draw_custom_inputs(surface)

        self.start_btn.draw(surface)

        self.stats_card.draw(surface)
        self._draw_stats_content(surface)

    def _draw_custom_inputs(self, surface: pygame.Surface) -> None:
        label_font = theme.font(14, "regular")

        def blit_left_middle(text, pos):
            surf = label_font.render(text, True, theme.TEXT_MUTED)
            rect = surf.get_rect(midleft=pos)
            surface.blit(surf, rect)

        blit_left_middle("Focus", self._focus_label_pos)
        self.focus_input.draw(surface)
        blit_left_middle("min", self._focus_min_pos)
        blit_left_middle("Break", self._break_label_pos)
        self.break_input.draw(surface)
        blit_left_middle("min", self._break_min_pos)

    def _draw_stats_content(self, surface: pygame.Surface) -> None:
        rect = self.stats_card.rect
        pad = theme.SPACE_LG

        heading = theme.font(13, "bold").render("TODAY", True, theme.TEXT_MUTED)
        surface.blit(heading, (rect.x + pad, rect.y + pad))

        sessions = self.today["sessions"]
        minutes = self.today["total_minutes"]

        value_font = theme.font(28, "bold")
        label_font = theme.font(13, "regular")

        s_value = value_font.render(str(sessions), True, theme.TEXT)
        s_label = label_font.render("sessions", True, theme.TEXT_MUTED)
        surface.blit(s_value, (rect.x + pad, rect.y + pad + 22))
        surface.blit(s_label, (rect.x + pad + s_value.get_width() + theme.SPACE_SM,
                               rect.y + pad + 22 + s_value.get_height() - s_label.get_height() - 4))

        m_value = value_font.render(str(minutes), True, theme.TEXT)
        m_label = label_font.render("min focused", True, theme.TEXT_MUTED)
        right_x = rect.x + rect.width - pad - m_label.get_width()
        m_value_x = right_x - theme.SPACE_SM - m_value.get_width()
        surface.blit(m_value, (m_value_x, rect.y + pad + 22))
        surface.blit(m_label, (right_x, rect.y + pad + 22 + m_value.get_height() - m_label.get_height() - 4))
