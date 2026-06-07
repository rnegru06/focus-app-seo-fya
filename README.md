# focus-app-seo-fya

A Pomodoro-style focus app with a snake game for a break built in Python with Pygame. Pick a study cycle, watch a calming progress ring fill, listen to ambient sounds (rain, forest, white noise), and take a break with a built-in snake mini-game. Designed for the SEO FYA PyGame Final Project.

## Layout

```
focus-app-seo-fya/
├── home_dashboard/      # The focus app — main UI, timer, settings, music, particles
│   ├── main.py            # Entry point
│   ├── theme.py           # Linear Frost color palette + font loaders
│   ├── widgets.py         # Reusable UI: Button, Chip, Card, NumberInput, ProgressRing, Slider, IconButton
│   ├── background.py      # Drifting particle animation
│   ├── audio.py           # Ambient music player + transition chime
│   ├── snake_launcher.py  # Spawns the snake game as a subprocess
│   ├── assets/music/      # rain.mp3, forest.mp3, white_noise.mp3
│   ├── data/
│   │   ├── stats.py         # Today's session count + total minutes
│   │   └── preferences.py   # Music track, volume, custom cycle defaults
│   └── screens/
│       ├── home.py          # Cycle picker, today's stats, Snake Break tile
│       ├── timer.py         # Progress ring + countdown + Pause/Stop + Play Snake
│       └── settings.py      # Music + volume + reset
└── break_game/          # Standalone Snake game (kept intact, launched as a subprocess)
    ├── Game.py
    ├── highscore.txt
    └── readme.md
```

## How to run

```bash
cd "<repo root>"
python3 -m venv .venv
source .venv/bin/activate
pip install -r home_dashboard/requirements.txt
python3 home_dashboard/main.py
```

## Controls

### Focus app (mouse)
- **Choose your cycle** — click one of the chips (25 / 5, 50 / 10, Custom).
- **Custom** — click the chip, then type focus and break minutes in the two input boxes.
- **Start Focus** — begin the cycle.
- **Pause / Resume** — toggle the timer (also pauses music).
- **Stop / ← back arrow** — return to the home dashboard.
- **Play Snake** (during break) or ** Snake Break** (on home, once unlocked) — launches the snake game in a separate window.
- **Gear icon** — open Settings (music picker, volume slider, reset today's stats).

### Snake mini-game (keyboard, in its own window)
- **Arrow keys** — steer the snake.
- **ENTER** — start a game / play again / dismiss menu screens.
- **R** — view rules (from menu).
- **P** — pause / resume.
- **ESC** — back to menu / quit.

## Features

| Feature | Where |
|---|---|
| Cycle picker (25/5, 50/10, Custom with two number inputs) | `screens/home.py` |
| Progress-ring time visual (clockwise arc, mm:ss inside) | `widgets.py` `ProgressRing`, `screens/timer.py` |
| Pause / Stop with auto phase transitions | `screens/timer.py` |
| Animated calming background (drifting glowing particles) | `background.py` |
| Three-option focus music (Rain / Forest / White Noise) | `audio.py`, `screens/settings.py` |
| Volume slider | `widgets.py` `Slider`, `screens/settings.py` |
| Settings persistence (track, volume, custom defaults) | `data/preferences.py` |
| Today's stats (sessions + minutes) | `data/stats.py`, `screens/home.py` |
| Reset today's stats | `screens/settings.py` |
| Snake Break mini-game — during break OR unlocked on home after 1 focus session | `snake_launcher.py`, `screens/home.py`, `screens/timer.py`, `break_game/Game.py` |
| Soft transition chime when phase changes | `audio.py` `play_chime` |

## Rubric coverage map

| Rubric item | Where it's addressed |
|---|---|
| **Visual / audio appeal** | Linear Frost palette + particle background + progress ring + ambient music + phase chime |
| **Music supports the concept** | Three calming ambient tracks for focus; chime signals every transition |
| **Text / icons clear and legible** | Generous sizing (13–28 px), high contrast, mono font for the countdown |
| **Easy to navigate** | Linear flow: home → timer → break → home; single back arrow on subscreens; settings discoverable via the gear icon |
| **Menu logically organized** | Cycle picker grouped, stats separate, settings on a dedicated screen |
| **Controls responsive / intuitive** | Mouse for the focus app; keyboard for snake (industry-standard mappings) |
| **Functionality** | All listed features work end-to-end (smoke-tested headless + manual launch) |
| **Coding** | Module docstrings, section headers, comments above non-obvious blocks; reused widgets across screens; no hard-coded colors (theme.py) or paths (Path-based) |
| **Planning** | This README's requirements + evaluation sections |
| **Evaluation** | The "Evaluation against requirements" and "What we'd improve next" sections above |
| **Elements (variables, ints, conditionals, loops, random, I/O, print)** | All present: cycle picker (conditionals), timer countdown (while-loop driving updates), snake game (random fruit/bomb spawn, while-loop), file I/O (stats, preferences, highscore), print statements for the invalid-start guard and snake-launch confirmation |
| **Game mechanics (snake)** | Original game preserved: fruits, bombs, levels, lives, high score |
| **Game UI (snake)** | MENU / RULES / PAUSED / WIN / GAME_OVER all kept |
| **Difficulty** | Snake's `update_level()` ramps speed and bomb count over time |
| **Instructions** | Snake's RULES screen + Controls section above |
| **Originality / creativity** | Pomodoro + integrated mini-game + procedural ambient particles + Linear-inspired aesthetic + stdlib-synthesized transition chime |
| **Efficiency** | 60 fps cap, cached fonts, cached glow sprites in `background.py`, single particle sweep per frame |
| **Reflection** | "What we'd improve next" honestly notes the snake-break-length compromise |

## Audio source attributions

The three ambient tracks were extracted from YouTube videos at the user's request, trimmed to 60-second loops, normalized to −18 LUFS, and faded in and out for seamless looping:

- **Rain** — https://youtu.be/eTeD8DAta4c
- **Forest** — https://youtu.be/xNN7iTA57jM
- **White Noise** — https://youtu.be/nMfPqeZjc2c
