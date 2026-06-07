"""BreakGameScreen — snake mini-game embedded inside the focus app window.

Renders the gameplay to an 800x600 internal surface, then blits it centered
inside the 1000x700 app window with a 100px side margin and a 50px top/
bottom margin. The top margin shows a back arrow + "Break ends in MM:SS"
(or just "Snake Break" in standalone mode).

Gameplay is a faithful re-implementation of the standalone Snake game in
../break_game/Game.py — same classes (Snake/Fruit/Bomb), same state names
(menu/rules/playing/paused/win/game_over), same scoring, same level ramp,
same high-score persistence (in our own data/highscore.txt so the original
game's file stays untouched).

ESC behavior (single rule, applied uniformly):
- In PLAYING: pause (same as P).
- In MENU/RULES/PAUSED/WIN/GAME_OVER: exit back to the focus app.

Time policy when launched from break (standalone=False):
- The break clock is owned by THIS screen and ticks in update(dt)
  regardless of game state. So paused, won, or game-over screens still
  drain the real-world break.
- When break time hits 0: auto-close — return a TimerScreen in focus phase.
- When user exits early: return a TimerScreen in break phase with whatever
  time is left.

When launched standalone (from home tile), there's no break timer. Exit
returns to HomeScreen."""
import os
import random
from pathlib import Path
from typing import Optional

import pygame

import theme
from widgets import IconButton


# --- frame layout ---

WINDOW_W, WINDOW_H = 1000, 700

GAME_W, GAME_H = 800, 600         # internal game surface size
GAME_X, GAME_Y = 100, 50          # blit offset inside the app window
GRID = 20                         # cell size; matches the original game

# --- game tuning (matches original) ---

TARGET_LEVEL = 5
STARTING_LIVES = 3

# --- game palette (matches the original — visually distinct from
# the focus app, signals "you're inside the mini-game now") ---

GAME_BG     = (15, 15, 20)
GRID_COLOR  = (25, 35, 25)
WHITE       = (240, 240, 240)
GREEN       = (46, 204, 113)
DARK_GREEN  = (39, 174, 96)
RED         = (231, 76, 60)
GOLD        = (255, 215, 0)
BLUE        = (52, 152, 219)
GRAY        = (120, 120, 120)

# --- state strings ---

MENU       = "menu"
RULES      = "rules"
PLAYING    = "playing"
PAUSED     = "paused"
WIN        = "win"
GAME_OVER  = "game_over"

# --- high score persistence (separate from break_game/highscore.txt) ---

_HIGHSCORE_FILE = Path(__file__).resolve().parent.parent / "data" / "highscore.txt"


def _load_high_score() -> int:
    if _HIGHSCORE_FILE.exists():
        try:
            return int(_HIGHSCORE_FILE.read_text().strip() or "0")
        except (ValueError, OSError):
            return 0
    return 0


def _save_high_score(score: int) -> None:
    try:
        _HIGHSCORE_FILE.write_text(str(int(score)))
    except OSError:
        pass


# =============================================================================
# Game entities
# =============================================================================

class Snake:
    """Grid-snapped snake body. dx/dy is per-step displacement, not per-second."""

    def __init__(self):
        self.body = [(400, 300), (380, 300), (360, 300)]
        self.dx = GRID
        self.dy = 0
        self.pending_growth = 0

    def change_direction(self, dx: int, dy: int) -> None:
        # Disallow 180° reversal — would self-collide instantly.
        if (dx, dy) == (-self.dx, -self.dy):
            return
        self.dx, self.dy = dx, dy

    def move(self) -> None:
        head_x, head_y = self.body[0]
        new_head = (head_x + self.dx, head_y + self.dy)
        self.body.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.pending_growth += amount

    def hit_wall(self) -> bool:
        x, y = self.body[0]
        return x < 0 or x >= GAME_W or y < 0 or y >= GAME_H

    def hit_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def reset_position(self) -> None:
        self.body = [(400, 300), (380, 300), (360, 300)]
        self.dx, self.dy = GRID, 0

    def draw(self, surface: pygame.Surface) -> None:
        for index, segment in enumerate(self.body):
            color = GREEN if index == 0 else DARK_GREEN
            pygame.draw.rect(surface, color, (segment[0], segment[1], GRID, GRID))


class Fruit:
    """Falls from the top. Four types, four point values."""

    TYPES = {
        "red":   {"color": RED,   "points": 10, "growth": 1},
        "gold":  {"color": GOLD,  "points": 25, "growth": 2},
        "blue":  {"color": BLUE,  "points": 50, "growth": 3},
        "green": {"color": GREEN, "points": 15, "growth": 1},  # rare: bonus life
    }

    def __init__(self):
        self.respawn()

    def respawn(self) -> None:
        self.x = random.randint(0, GAME_W // GRID - 1) * GRID
        self.y = -20
        # Type roll matches the original odds.
        roll = random.random()
        if   roll < 0.60: self.type = "red"
        elif roll < 0.85: self.type = "gold"
        elif roll < 0.97: self.type = "blue"
        else:             self.type = "green"
        self.speed = random.randint(2, 4)

    def update(self) -> None:
        self.y += self.speed

    def draw(self, surface: pygame.Surface) -> None:
        color = self.TYPES[self.type]["color"]
        pygame.draw.circle(surface, color, (self.x + GRID // 2, self.y + GRID // 2), 8)


class Bomb:
    """Falls from the top. Touching one costs a life."""

    def __init__(self):
        self.respawn()

    def respawn(self) -> None:
        self.x = random.randint(0, GAME_W // GRID - 1) * GRID
        self.y = random.randint(-500, -20)
        self.speed = random.randint(3, 6)

    def update(self) -> None:
        self.y += self.speed

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, GRAY, (self.x, self.y, GRID, GRID))


# =============================================================================
# BreakGameScreen — embeds the game in the focus app
# =============================================================================

class BreakGameScreen:
    def __init__(
        self,
        focus_minutes: int = 25,
        break_minutes: int = 5,
        time_left_seconds: float = 300.0,
        custom_focus: int = 25,
        custom_break: int = 5,
        selected_cycle: str = "25/5",
        standalone: bool = False,
    ):
        # --- handoff state from parent timer ---
        self._focus_minutes = int(focus_minutes)
        self._break_minutes = int(break_minutes)
        self._custom_focus = custom_focus
        self._custom_break = custom_break
        self._selected_cycle = selected_cycle
        self.standalone = standalone

        # The break clock. Ignored when standalone.
        self._break_time_left = float(time_left_seconds)

        # --- game state ---
        self.game_state = MENU
        self.snake = Snake()
        self.fruits: list[Fruit] = [Fruit()]
        self.bombs: list[Bomb] = [Bomb(), Bomb()]
        self.score = 0
        self.level = 1
        self.lives = STARTING_LIVES
        self.snake_speed = 8           # snake step rate factor; bumps by 2 per level
        self.end_reason = ""
        self.high_score = _load_high_score()

        # Snake-move timing — accumulator decrements toward a step.
        self._move_accum = 0.0

        # Cache fonts used inside the game canvas.
        self._font       = pygame.font.SysFont("consolas", 22)
        self._small_font = pygame.font.SysFont("consolas", 18)
        self._big_font   = pygame.font.SysFont("consolas", 50)

        # Internal canvas — all snake/fruit/bomb draws go here, then blit.
        self._canvas = pygame.Surface((GAME_W, GAME_H))

        self._next_screen = None

        # Frame chrome (lives in the focus-app window margin, not the canvas).
        self.back_btn = IconButton(
            pygame.Rect(18, 18, 36, 36),
            glyph="←",
            on_click=self._exit_to_app,
        )

    # ---------------------------------------------------------------
    # transitions / exit policy
    # ---------------------------------------------------------------

    def _exit_to_app(self) -> None:
        """User pressed back / ESC from a non-PLAYING state."""
        if self.standalone:
            from screens.home import HomeScreen
            self._next_screen = HomeScreen(
                custom_focus=self._custom_focus,
                custom_break=self._custom_break,
            )
        else:
            # Return to the timer in break phase with the remaining time.
            from screens.timer import TimerScreen, PHASE_BREAK
            t = TimerScreen(
                focus_minutes=self._focus_minutes,
                break_minutes=self._break_minutes,
                custom_focus=self._custom_focus,
                custom_break=self._custom_break,
                selected_cycle=self._selected_cycle,
            )
            t.phase = PHASE_BREAK
            t.time_left = max(0.0, self._break_time_left)
            t._phase_total = float(self._break_minutes * 60) or 1.0
            from screens.timer import BREAK_COLOR
            t.ring.color = BREAK_COLOR
            self._next_screen = t

    def _auto_close_break_ended(self) -> None:
        """Called when the break clock hits 0 mid-game. Returns to a fresh
        focus phase — break is over, time to study."""
        from screens.timer import TimerScreen
        self._next_screen = TimerScreen(
            focus_minutes=self._focus_minutes,
            break_minutes=self._break_minutes,
            custom_focus=self._custom_focus,
            custom_break=self._custom_break,
            selected_cycle=self._selected_cycle,
        )

    # ---------------------------------------------------------------
    # game-logic helpers (mirror the original's modular functions)
    # ---------------------------------------------------------------

    def _reset_game(self) -> None:
        self.snake = Snake()
        self.fruits = [Fruit()]
        self.bombs = [Bomb(), Bomb()]
        self.score = 0
        self.level = 1
        self.lives = STARTING_LIVES
        self.snake_speed = 8
        self.end_reason = ""
        self._move_accum = 0.0

    def _lose_life(self, reason: str) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.end_reason = reason
            self.game_state = GAME_OVER
        else:
            self.snake.reset_position()

    def _add_score(self, amount: int) -> None:
        self.score += amount
        if self.score > self.high_score:
            self.high_score = self.score
            _save_high_score(self.high_score)

    def _snake_hits_object(self, obj_x: int, obj_y: int) -> bool:
        head_x, head_y = self.snake.body[0]
        return abs(head_x - obj_x) < GRID and abs(head_y - obj_y) < GRID

    def _update_fruits(self) -> None:
        for fruit in self.fruits[:]:
            fruit.update()
            # Fruit escaped past the bottom — life lost.
            if fruit.y > GAME_H:
                self.fruits.remove(fruit)
                self._lose_life("You let too many fruits escape!")
                self.fruits.append(Fruit())
                continue
            # Snake collects fruit.
            if self._snake_hits_object(fruit.x, fruit.y):
                data = Fruit.TYPES[fruit.type]
                self._add_score(data["points"])
                self.snake.grow(data["growth"])
                # Green fruit grants a bonus life (capped at 5).
                if fruit.type == "green":
                    self.lives = min(5, self.lives + 1)
                self.fruits.remove(fruit)
                self.fruits.append(Fruit())

    def _update_bombs(self) -> None:
        for bomb in self.bombs:
            bomb.update()
            if bomb.y > GAME_H:
                bomb.respawn()
            if self._snake_hits_object(bomb.x, bomb.y):
                bomb.respawn()
                self._lose_life("You hit a bomb!")

    def _update_level(self) -> None:
        # Original formula: 1 level per 5 segments of snake length, capped.
        new_level = min(TARGET_LEVEL, len(self.snake.body) // 5 + 1)
        if new_level > self.level:
            self.level = new_level
            self.snake_speed += 2
            self.bombs.append(Bomb())
            for fruit in self.fruits:
                fruit.speed += 1

    def _check_win(self) -> None:
        if self.level >= TARGET_LEVEL:
            self.game_state = WIN

    def _tick_snake(self, dt: float) -> None:
        """Run one step of game logic if enough time has elapsed since the
        last step. dt is seconds since last frame."""
        # move_delay in seconds: same formula as original (ticks→ms→s).
        move_delay_ms = max(40, 180 - (self.snake_speed * 10))
        move_delay = move_delay_ms / 1000.0
        self._move_accum += dt
        while self._move_accum >= move_delay and self.game_state == PLAYING:
            self._move_accum -= move_delay
            self.snake.move()
            # Wall collision
            if self.snake.hit_wall():
                self._lose_life("You hit the wall!")
                if self.game_state != PLAYING:
                    return
            self._update_fruits()
            self._update_bombs()
            self._update_level()
            self._check_win()
            if self.game_state != PLAYING:
                return
            if self.snake.hit_self():
                self._lose_life("You ran into yourself!")

    # ---------------------------------------------------------------
    # screen API
    # ---------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        # Mouse click on the back arrow (works from any state).
        consumed = self.back_btn.handle_event(event)
        if consumed:
            nxt = self._next_screen
            self._next_screen = None
            return nxt

        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        nxt = self._next_screen
        self._next_screen = None
        return nxt

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        key = event.key

        if self.game_state == MENU:
            if key == pygame.K_RETURN:
                self._reset_game()
                self.game_state = PLAYING
            elif key == pygame.K_r:
                self.game_state = RULES
            elif key == pygame.K_ESCAPE:
                self._exit_to_app()

        elif self.game_state == RULES:
            if key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.game_state = MENU

        elif self.game_state == PLAYING:
            if   key == pygame.K_UP:    self.snake.change_direction(0, -GRID)
            elif key == pygame.K_DOWN:  self.snake.change_direction(0,  GRID)
            elif key == pygame.K_LEFT:  self.snake.change_direction(-GRID, 0)
            elif key == pygame.K_RIGHT: self.snake.change_direction( GRID, 0)
            elif key == pygame.K_p:     self.game_state = PAUSED
            elif key == pygame.K_ESCAPE: self.game_state = PAUSED

        elif self.game_state == PAUSED:
            if key == pygame.K_p:
                self.game_state = PLAYING
            elif key == pygame.K_ESCAPE:
                self._exit_to_app()

        elif self.game_state == WIN:
            if key == pygame.K_RETURN:
                self._reset_game()
                self.game_state = PLAYING
            elif key == pygame.K_ESCAPE:
                self._exit_to_app()

        elif self.game_state == GAME_OVER:
            if key == pygame.K_RETURN:
                self._reset_game()
                self.game_state = PLAYING
            elif key == pygame.K_ESCAPE:
                self._exit_to_app()

    def update(self, dt: float) -> None:
        # Drain the real-world break clock regardless of game state.
        if not self.standalone:
            self._break_time_left -= dt
            if self._break_time_left <= 0:
                self._auto_close_break_ended()
                return

        if self.game_state == PLAYING:
            self._tick_snake(dt)

    def draw(self, surface: pygame.Surface) -> None:
        # --- frame chrome (in the app's window margin, not the canvas) ---
        self.back_btn.draw(surface)
        self._draw_frame_header(surface)

        # --- game canvas ---
        self._canvas.fill(GAME_BG)
        if self.game_state == MENU:
            self._draw_menu()
        elif self.game_state == RULES:
            self._draw_rules()
        elif self.game_state == PLAYING:
            self._draw_game()
        elif self.game_state == PAUSED:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.game_state == WIN:
            self._draw_win()
        elif self.game_state == GAME_OVER:
            self._draw_game_over()

        # Blit canvas centered into the app window.
        surface.blit(self._canvas, (GAME_X, GAME_Y))

        # Subtle border around the canvas so it reads as a panel.
        border_rect = pygame.Rect(GAME_X - 1, GAME_Y - 1, GAME_W + 2, GAME_H + 2)
        pygame.draw.rect(surface, theme.SURFACE_2, border_rect, width=1, border_radius=4)

    # ---------------------------------------------------------------
    # frame header (in the focus-app window above the canvas)
    # ---------------------------------------------------------------

    def _draw_frame_header(self, surface: pygame.Surface) -> None:
        if self.standalone:
            text = "Snake Break"
            color = theme.TEXT_MUTED
        else:
            secs = max(0, int(self._break_time_left + 0.5))
            m, s = divmod(secs, 60)
            text = f"Break ends in {m:02d}:{s:02d}"
            color = theme.TEXT
        label = theme.font(15, "bold").render(text, True, color)
        surface.blit(label, label.get_rect(midright=(WINDOW_W - theme.SPACE_LG, 36)))

    # ---------------------------------------------------------------
    # canvas draw helpers (render to self._canvas)
    # ---------------------------------------------------------------

    def _blit_text(self, text: str, x: int, y: int, color=WHITE, font=None) -> None:
        f = font or self._font
        self._canvas.blit(f.render(text, True, color), (x, y))

    def _draw_menu(self) -> None:
        self._blit_text("FOCUS BREAK SNAKE", 170, 120, GREEN, self._big_font)
        self._blit_text("Press ENTER to Start", 250, 260)
        self._blit_text("Press R for Rules",    270, 310)
        self._blit_text(f"High Score: {self.high_score}", 280, 380, GOLD)
        self._blit_text("ESC = Back to focus app", 230, 460, GRAY, self._small_font)

    def _draw_rules(self) -> None:
        lines = [
            "RULES", "",
            "Eat fruits to grow.",
            "Reach Level 5 to win.",
            "Do not hit bombs.",
            "Do not hit walls.",
            "Do not let fruit escape.",
            "You have 3 lives.",
            "",
            "P = Pause", "",
            "ENTER = Back",
        ]
        y = 80
        for line in lines:
            self._blit_text(line, 120, y)
            y += 35

    def _draw_game(self) -> None:
        # grid background
        for x in range(0, GAME_W, GRID):
            pygame.draw.line(self._canvas, GRID_COLOR, (x, 0), (x, GAME_H))
        for y in range(0, GAME_H, GRID):
            pygame.draw.line(self._canvas, GRID_COLOR, (0, y), (GAME_W, y))
        self.snake.draw(self._canvas)
        for fruit in self.fruits:
            fruit.draw(self._canvas)
        for bomb in self.bombs:
            bomb.draw(self._canvas)
        self._draw_hud()

    def _draw_hud(self) -> None:
        self._blit_text(f"Score: {self.score}",                 10,  10)
        self._blit_text(f"Level: {self.level}/{TARGET_LEVEL}",  10,  40)
        # Original used emoji hearts; SysFont may not render them — use ASCII.
        hearts = "♥ " * self.lives
        self._blit_text(f"Lives: {hearts.strip()}",             10,  70, RED)
        self._blit_text(f"High Score: {self.high_score}",       600, 10, GOLD)

    def _draw_pause_overlay(self) -> None:
        # Dim the game and overlay the PAUSED text.
        overlay = pygame.Surface((GAME_W, GAME_H))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self._canvas.blit(overlay, (0, 0))
        self._blit_text("PAUSED",            290, 220, WHITE, self._big_font)
        self._blit_text("Press P to Resume", 270, 310)
        self._blit_text("ESC to exit Snake", 270, 350, GRAY,  self._small_font)

    def _draw_win(self) -> None:
        self._blit_text("YOU WON!",                250, 150, GOLD, self._big_font)
        self._blit_text(f"Reached Level {self.level}", 260, 250)
        self._blit_text(f"Final Score: {self.score}", 260, 300)
        self._blit_text("ENTER = Play Again",       240, 380)
        self._blit_text("ESC = Exit",                250, 430)

    def _draw_game_over(self) -> None:
        self._blit_text("GAME OVER",                  220, 140, RED, self._big_font)
        self._blit_text(self.end_reason,              180, 240, WHITE)
        self._blit_text(f"Score: {self.score}",       250, 300)
        self._blit_text(f"Level Reached: {self.level}", 250, 340)
        self._blit_text("ENTER = Retry",              250, 420)
        self._blit_text("ESC = Exit",                  250, 460)
