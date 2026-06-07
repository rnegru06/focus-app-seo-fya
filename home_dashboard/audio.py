"""Audio singleton — manages the ambient music player and the
phase-transition chime. The three ambient tracks (rain, forest, white_noise)
are MP3 loops in assets/music/. The chime is a tiny stdlib-generated
two-note ping. All audio plays through pygame.mixer."""
import array
import math
import os
from pathlib import Path
from typing import Optional

import pygame


# --- module-level state ---

TRACKS = ["rain", "forest", "white_noise"]
_MUSIC_DIR = Path(__file__).resolve().parent / "assets" / "music"

_current_track: Optional[str] = None   # "rain"/"forest"/"white_noise"/"off"
_volume: float = 0.4
_paused: bool = False
_chime: Optional[pygame.mixer.Sound] = None
_ready: bool = False


# --- public API ---

def init() -> None:
    """Verify the music files exist and pre-build the transition chime.
    Call once after pygame.mixer.init()."""
    global _ready, _chime
    missing = [t for t in TRACKS if not (_MUSIC_DIR / f"{t}.wav").exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing music files: {missing}. Expected .wav in {_MUSIC_DIR}."
        )
    _chime = _build_chime()
    _ready = True


def list_tracks() -> list[str]:
    return list(TRACKS)


def current() -> str:
    """Currently selected track ('rain'/'forest'/'white_noise') or 'off'."""
    return _current_track or "off"


def play(name: str) -> None:
    """Switch to a track or 'off' to stop. Crossfades between tracks."""
    global _current_track, _paused
    if not _ready:
        return
    if name == "off":
        pygame.mixer.music.fadeout(400)
        _current_track = "off"
        _paused = False
        return
    if name not in TRACKS:
        raise ValueError(f"Unknown track {name!r}; expected one of {TRACKS} or 'off'.")
    path = _MUSIC_DIR / f"{name}.wav"
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.set_volume(_volume)
    # loops=-1: loop forever. fade_ms gives a soft cross with the previous track.
    pygame.mixer.music.play(loops=-1, fade_ms=400)
    _current_track = name
    _paused = False


def set_volume(v: float) -> None:
    """Set music volume in [0.0, 1.0]. Affects future plays and the active stream."""
    global _volume
    _volume = max(0.0, min(1.0, float(v)))
    if _ready:
        pygame.mixer.music.set_volume(_volume)


def get_volume() -> float:
    return _volume


def pause() -> None:
    """Pause music playback (used when timer is paused)."""
    global _paused
    if _ready and _current_track and _current_track != "off":
        pygame.mixer.music.pause()
        _paused = True


def resume() -> None:
    global _paused
    if _ready and _paused:
        pygame.mixer.music.unpause()
        _paused = False


def play_chime() -> None:
    """Play the short transition chime once. Safe to call any time after init()."""
    if _ready and _chime is not None:
        _chime.set_volume(min(1.0, _volume + 0.3))  # chime is always audible
        _chime.play()


# --- chime synthesis (stdlib only) ---

def _build_chime() -> pygame.mixer.Sound:
    """Generate a soft two-note ping (E5 then A5) with linear decay.
    Total length ~0.5 s. Pure stdlib — math.sin into an int16 array.
    Samples are generated at whatever rate pygame.mixer is using so the
    chime plays at its intended pitch."""
    mixer_info = pygame.mixer.get_init()
    sample_rate = mixer_info[0] if mixer_info else 44100
    note1_freq = 659.25   # E5
    note2_freq = 880.00   # A5
    note_len   = 0.20     # seconds each
    gap        = 0.05     # seconds between notes
    amp        = 0.25     # 0..1
    total = note_len * 2 + gap

    n_total = int(total * sample_rate)
    samples = array.array('h', [0] * (n_total * 2))  # stereo int16

    n_note = int(note_len * sample_rate)
    n_gap  = int(gap * sample_rate)

    def write_note(start_idx: int, freq: float):
        # Linear amplitude decay from amp to 0 over the note's length.
        for i in range(n_note):
            envelope = 1.0 - (i / n_note)
            value = int(32767 * amp * envelope * math.sin(2 * math.pi * freq * i / sample_rate))
            samples[2 * (start_idx + i)]     = value
            samples[2 * (start_idx + i) + 1] = value

    write_note(0, note1_freq)
    write_note(n_note + n_gap, note2_freq)

    return pygame.mixer.Sound(buffer=samples.tobytes())
