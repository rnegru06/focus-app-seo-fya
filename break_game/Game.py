import pygame
import random
import os

pygame.init()

#SCREEEN
WIDTH = 800
HEIGHT = 600
GRID = 20
FPS = 60

BREAK_TIME = 180 #3 mins
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Focus Break Snake Deluxe")

clock = pygame.time.Clock()

#COlors
BLACK = (15, 15, 20)
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

    # FIX 1: moved hit_self inside the Snake class as a proper method
    def hit_self(self):
        return self.body[0] in self.body[1:]

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

# RESET GAME

def reset_game():

    global snake
    global fruits
    global bombs

    global score
    global level
    global lives

    global snake_speed
    global end_reason

    global start_ticks

    snake = Snake()

    fruits = [Fruit()]
    bombs = [Bomb(), Bomb()]

    score = 0
    level = 1
    lives = STARTING_LIVES

    snake_speed = 8

    end_reason = ""

    start_ticks = pygame.time.get_ticks()


# Game TIMER

def get_time_remaining():

    elapsed = (
        pygame.time.get_ticks() -
        start_ticks
    ) // 1000

    return max(
        0,
        BREAK_TIME - elapsed
    )


# The LEVELS SYSTEM

def update_level():

    global level
    global bombs
    global snake_speed

    new_level = min(
        TARGET_LEVEL,
        len(snake.body) // 5 + 1
    )

    if new_level > level:

        level = new_level

        # harder every level
        snake_speed += 2

        bombs.append(Bomb())

        # fruit falls faster
        for fruit in fruits:
            fruit.speed += 1



# LIFE SYSTEM


def lose_life(reason):

    global lives
    global state
    global end_reason

    lives -= 1

    if lives <= 0:

        end_reason = reason
        state = GAME_OVER

    else:

        # reset snake position
        snake.body = [
            (400, 300),
            (380, 300),
            (360, 300)
        ]

        snake.dx = GRID
        snake.dy = 0


# SCORE SYSTEM

def add_score(amount):

    global score
    global high_score

    score += amount

    if score > high_score:

        high_score = score
        save_high_score(high_score)

# COLLISION HELPERS


def snake_hits_object(obj_x, obj_y):

    head_x, head_y = snake.body[0]

    return (
        abs(head_x - obj_x) < GRID
        and
        abs(head_y - obj_y) < GRID
    )


# UPDATE FRUITS

def update_fruits():

    # FIX 2: added global lives so the green fruit life bonus actually applies
    global lives

    for fruit in fruits[:]:

        fruit.update()

        # fruit escaped
        if fruit.y > HEIGHT:

            fruits.remove(fruit)

            lose_life(
                "You let too many fruits escape!"
            )

            fruits.append(Fruit())

            continue

        # collected fruit
        if snake_hits_object(
                fruit.x,
                fruit.y):

            data = Fruit.TYPES[
                fruit.type
            ]

            add_score(
                data["points"]
            )

            snake.grow(
                data["growth"]
            )

            # rare bonus life fruit
            if fruit.type == "green":
                lives = min(5, lives + 1)

            fruits.remove(fruit)

            fruits.append(Fruit())


# UPDATE BOMBS


def update_bombs():

    for bomb in bombs:

        bomb.update()

        # recycle bomb
        if bomb.y > HEIGHT:
            bomb.respawn()

        # bomb collision
        if snake_hits_object(
                bomb.x,
                bomb.y):

            bomb.respawn()

            lose_life(
                "You hit a bomb!"
            )



# WIN CONDITION


def check_win():

    global state

    if level >= TARGET_LEVEL:
        state = WIN



# TIMEOUT CONDITION


def check_time():

    global state
    global end_reason

    if get_time_remaining() <= 0:

        end_reason = (
            "Time ran out!"
        )

        state = GAME_OVER



# UPDATE GAME


def update_game():

    snake.move()

    # wall collision
    if snake.hit_wall():

        lose_life(
            "You hit the wall!"
        )

    update_fruits()

    update_bombs()

    update_level()

    check_win()

    check_time()



# HUD


def draw_hud():

    draw_text(
        f"Score: {score}",
        10,
        10
    )

    draw_text(
        f"Level: {level}/{TARGET_LEVEL}",
        10,
        40
    )

    draw_text(
        f"Lives: {'❤️' * lives}",
        10,
        70
    )

    draw_text(
        f"Time Left: {get_time_remaining()}s",
        10,
        100
    )

    draw_text(
        f"High Score: {high_score}",
        600,
        10,
        GOLD
    )



# DRAW GAME


def draw_game():

    screen.fill(BLACK)

    # grid background
    for x in range(
            0,
            WIDTH,
            GRID):

        pygame.draw.line(
            screen,
            (25, 35, 25),
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(
            0,
            HEIGHT,
            GRID):

        pygame.draw.line(
            screen,
            (25, 35, 25),
            (0, y),
            (WIDTH, y)
        )

    snake.draw(screen)

    for fruit in fruits:
        fruit.draw(screen)

    for bomb in bombs:
        bomb.draw(screen)

    draw_hud()

# PAUSE SCREEN

def draw_pause():

    draw_game()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT)
    )

    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))

    screen.blit(overlay, (0, 0))

    draw_text(
        "PAUSED",
        290,
        220,
        WHITE,
        BIG_FONT
    )

    draw_text(
        "Press P to Resume",
        270,
        310
    )



# WIN SCREEN


def draw_win():

    screen.fill(BLACK)

    draw_text(
        "YOU WON!",
        250,
        150,
        GOLD,
        BIG_FONT
    )

    draw_text(
        f"Reached Level {level}",
        260,
        250
    )

    draw_text(
        f"Final Score: {score}",
        260,
        300
    )

    draw_text(
        "ENTER = Play Again",
        240,
        380
    )

    draw_text(
        "ESC = Main Menu",
        250,
        430
    )


# GAME IS OVER SCREEN


def draw_game_over():

    screen.fill(BLACK)

    draw_text(
        "GAME OVER",
        220,
        140,
        RED,
        BIG_FONT
    )

    draw_text(
        end_reason,
        180,
        240,
        WHITE
    )

    draw_text(
        f"Score: {score}",
        250,
        300
    )

    draw_text(
        f"Level Reached: {level}",
        250,
        340
    )

    draw_text(
        "ENTER = Retry",
        250,
        420
    )

    draw_text(
        "ESC = Main Menu",
        250,
        460
    )


# SNAKE MOVEMENT TIMER


last_move_time = pygame.time.get_ticks()


def handle_snake_movement():

    global last_move_time

    current = pygame.time.get_ticks()

    move_delay = max(
        40,
        180 - (snake_speed * 10)
    )

    if current - last_move_time >= move_delay:

        # FIX 3: check hit_self after move (inside update_game),
        # and call it correctly with () — removed the broken out-of-order call
        update_game()

        if snake.hit_self():
            lose_life("You ran into Yourself!")

        last_move_time = current



# START FRESH NEW GAME


reset_game()

# MAIN LOOP


running = True

while running:

    clock.tick(FPS)


    # EVENTS


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:


            # MENU


            if state == MENU:

                if event.key == pygame.K_RETURN:

                    reset_game()
                    state = PLAYING

                elif event.key == pygame.K_r:

                    state = RULES

                elif event.key == pygame.K_ESCAPE:

                    running = False


            # RULES


            elif state == RULES:

                if event.key == pygame.K_RETURN:

                    state = MENU


            # PLAYING


            elif state == PLAYING:

                if event.key == pygame.K_UP:

                    snake.change_direction(
                        0,
                        -GRID
                    )

                elif event.key == pygame.K_DOWN:

                    snake.change_direction(
                        0,
                        GRID
                    )

                elif event.key == pygame.K_LEFT:

                    snake.change_direction(
                        -GRID,
                        0
                    )

                elif event.key == pygame.K_RIGHT:

                    snake.change_direction(
                        GRID,
                        0
                    )

                elif event.key == pygame.K_p:

                    state = PAUSED


            # PAUSED


            elif state == PAUSED:

                if event.key == pygame.K_p:

                    state = PLAYING

            # ==================
            # WIN
            # ==================

            elif state == WIN:

                if event.key == pygame.K_RETURN:

                    reset_game()
                    state = PLAYING

                elif event.key == pygame.K_ESCAPE:

                    state = MENU


            # GAME OVER


            elif state == GAME_OVER:

                if event.key == pygame.K_RETURN:

                    reset_game()
                    state = PLAYING

                elif event.key == pygame.K_ESCAPE:

                    state = MENU


    # UPDATE


    if state == PLAYING:

        handle_snake_movement()


    # DRAW


    if state == MENU:

        draw_menu()

    elif state == RULES:

        draw_rules()

    elif state == PLAYING:

        draw_game()

    elif state == PAUSED:

        draw_pause()

    elif state == WIN:

        draw_win()

    elif state == GAME_OVER:

        draw_game_over()

    pygame.display.flip()

pygame.quit()