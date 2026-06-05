import pygame
import random
import os

pygame.init()

#SCREEEN
WIDTH = 800
HEIGHT = 600
GRIDD = 20
FPS = 60

Break_Time = 180 #3 mins
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Focus Break Snake Deluxe")

clock = pygame.time.Clock()

#COlors
LACK = (15, 15, 20)
WHITE = (240, 240, 240)

GREEN = (46, 204, 113)
DARK_GREEN = (39, 174, 96)

RED = (231, 76, 60)
GOLD = (255, 215, 0)
BLUE = (52, 152, 219)

GRAY = (120, 120, 120)

#FONTS
FONT = pygame.font.SysFont("consolas", 22)
SMALL_FONT = pygame.font.SysFont("consolas", 18)
BIG_FONT = pygame.font.SysFont("consolas", 50)

#STATES
MENU = "menu"
RULES = "rules"
PLAYING = "playing"
PAUSED = "paused"
WIN = "win"
GAME_OVER = "game_over"

state = MENU

#HIGH SCORE

HIGH_SCORE_FILE = "highscore.txt"
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            try:
                return int(file.read())
            except:
                return 0
    return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))


high_score = load_high_score()

#GAME SETTINGS
TARGET_LEVEL = 5
STARTING_LIVES = 3

# THE SNAKE

class Snake:

    def __init__(self):
        self.body = [
            (400, 300),
            (380, 300),
            (360, 300)
        ]

        self.dx = GRID
        self.dy = 0

        self.pending_growth = 0

    def change_direction(self, dx, dy):

        if (dx, dy) == (-self.dx, -self.dy):
            return

        self.dx = dx
        self.dy = dy

    def move(self):

        head_x, head_y = self.body[0]

        new_head = (
            head_x + self.dx,
            head_y + self.dy
        )

        self.body.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.pending_growth += amount

    def hit_wall(self):

        x, y = self.body[0]

        return (
                x < 0 or
                x >= WIDTH or
                y < 0 or
                y >= HEIGHT
        )

    def draw(self, surface):

        for index, segment in enumerate(self.body):

            color = GREEN if index == 0 else DARK_GREEN

            pygame.draw.rect(
                surface,
                color,
                (segment[0], segment[1], GRID, GRID)
            )

#FRUITS
class Fruit:

    TYPES = {

        "red": {
            "color": RED,
            "points": 10,
            "growth": 1
        },

        "gold": {
            "color": GOLD,
            "points": 25,
            "growth": 2
        },

        "blue": {
            "color": BLUE,
            "points": 50,
            "growth": 3
        },

        "green": {
            "color": GREEN,
            "points": 15,
            "growth": 1
        }
    }

    def __init__(self):
        self.respawn()

    def respawn(self):

        self.x = random.randint(
            0,
            WIDTH // GRID - 1
        ) * GRID

        self.y = -20

        roll = random.random()

        if roll < 0.60:
            self.type = "red"

        elif roll < 0.85:
            self.type = "gold"

        elif roll < 0.97:
            self.type = "blue"

        else:
            self.type = "green"

        self.speed = random.randint(2, 4)

    def update(self):
        self.y += self.speed

    def draw(self, surface):

        color = self.TYPES[self.type]["color"]

        pygame.draw.circle(
            surface,
            color,
            (self.x + GRID // 2,
             self.y + GRID // 2),
            8
        )
#BOMBS
class Bomb:

    def __init__(self):
        self.respawn()

    def respawn(self):

        self.x = random.randint(
            0,
            WIDTH // GRID - 1
        ) * GRID

        self.y = random.randint(-500, -20)

        self.speed = random.randint(3, 6)

    def update(self):
        self.y += self.speed

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            GRAY,
            (self.x, self.y, GRID, GRID)
        )

#GAMES VARIABLES
snake = Snake()

fruits = [Fruit()]
bombs = [Bomb(), Bomb()]

score = 0
level = 1
lives = STARTING_LIVES

snake_speed = 8

end_reason = ""

start_ticks = pygame.time.get_ticks()

#DRAW HELPERS
def draw_text(text,
              x,
              y,
              color=WHITE,
              font=FONT):

    image = font.render(text, True, color)

    screen.blit(image, (x, y))

#MENU SCREEN
def draw_menu():

    screen.fill(BLACK)

    draw_text(
        "FOCUS BREAK SNAKE",
        170,
        120,
        GREEN,
        BIG_FONT
    )

    draw_text(
        "Press ENTER to Start",
        250,
        260
    )

    draw_text(
        "Press R for Rules",
        270,
        310
    )

    draw_text(
        f"High Score: {high_score}",
        280,
        380,
        GOLD
    )
#RULES
def draw_rules():

    screen.fill(BLACK)

    lines = [

        "RULES",

        "",

        "Eat fruits to grow.",

        "Reach Level 5 to win.",

        "Do not hit bombs.",

        "Do not hit walls.",

        "Do not let fruit escape.",

        "You have 3 lives.",

        "",

        "P = Pause",

        "",

        "ENTER = Back"
    ]

    y = 80

    for line in lines:

        draw_text(line, 120, y)

        y += 35




