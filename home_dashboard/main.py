"""Focus — entry point. Initializes Pygame + audio, loads preferences,
holds the screen router, and draws the particle background each frame
behind the active screen."""
import pygame

import theme
import audio
import background
from data import preferences
from screens.home import HomeScreen, WINDOW_W, WINDOW_H


def main() -> None:
    # --- init ---
    # 44.1 kHz matches the music tracks (and most system audio) so MP3
    # playback isn't resampled/silenced. Buffer=512 keeps the chime snappy.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    pygame.mixer.set_num_channels(8)

    pygame.display.set_caption("Focus")
    surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    # --- audio + preferences ---
    audio.init()
    prefs = preferences.load()
    audio.set_volume(prefs["volume"])
    audio.play(prefs["music_track"])

    # --- particle background, drawn before every screen ---
    bg = background.ParticleBackground(WINDOW_W, WINDOW_H)

    # --- main loop ---
    current = HomeScreen()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            next_screen = current.handle_event(event)
            if next_screen is not None:
                current = next_screen

        bg.update(dt)
        current.update(dt)

        surface.fill(theme.BG)
        bg.draw(surface)
        current.draw(surface)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
