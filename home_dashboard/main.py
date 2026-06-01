"""Focus — entry point. Holds the screen router and main loop."""
import pygame

import theme
from screens.home import HomeScreen, WINDOW_W, WINDOW_H


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Focus")
    surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

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

        current.update(dt)
        surface.fill(theme.BG)
        current.draw(surface)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
