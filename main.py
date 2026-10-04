"""AI Escape Grid: reach the exit before the enemy or the clock catches you."""

from collections import deque
import random
import sys

import pygame


# Window and board settings
SCREEN_WIDTH = 980
SCREEN_HEIGHT = 680
GRID_SIZE = 10
CELL_SIZE = 58
GRID_X = 30
GRID_Y = 82

# Colors
BACKGROUND = (17, 29, 34)
PANEL = (26, 42, 47)
GRID_COLOR = (46, 65, 69)
FLOOR_COLOR = (30, 48, 52)
WALL_COLOR = (67, 91, 89)
WALL_HIGHLIGHT = (86, 112, 105)
TEXT_COLOR = (232, 241, 235)
MUTED_TEXT = (155, 178, 174)
PLAYER_COLOR = (85, 222, 190)
ENEMY_COLOR = (250, 111, 91)
EXIT_COLOR = (255, 207, 92)
BUTTON_COLOR = (48, 77, 75)
EASY_COLOR = (85, 222, 190)
MEDIUM_COLOR = (255, 207, 92)
HARD_COLOR = (250, 111, 91)

SCENARIO_THEMES = [
    {
        "name": "MOSSY GREENHOUSE",
        "background": (15, 31, 29),
        "panel": (27, 48, 42),
        "grid": (57, 83, 68),
        "floor": (31, 54, 43),
        "wall": (76, 107, 72),
        "wall_highlight": (122, 151, 94),
        "button": (46, 75, 61),
        "accent": (153, 207, 123),
    },
    {
        "name": "FROST QUARTER",
        "background": (18, 30, 47),
        "panel": (31, 47, 66),
        "grid": (70, 99, 119),
        "floor": (39, 61, 79),
        "wall": (91, 120, 133),
        "wall_highlight": (145, 177, 183),
        "button": (45, 72, 89),
        "accent": (134, 202, 218),
    },
    {
        "name": "DUST DISTRICT",
        "background": (39, 26, 23),
        "panel": (57, 39, 32),
        "grid": (98, 69, 52),
        "floor": (74, 51, 39),
        "wall": (133, 86, 57),
        "wall_highlight": (187, 128, 77),
        "button": (89, 57, 39),
        "accent": (229, 166, 105),
    },
    {
        "name": "TOXIC YARD",
        "background": (24, 28, 27),
        "panel": (39, 47, 40),
        "grid": (83, 107, 66),
        "floor": (47, 62, 39),
        "wall": (105, 128, 63),
        "wall_highlight": (163, 187, 78),
        "button": (59, 77, 42),
        "accent": (192, 213, 106),
    },
]
SCENARIO_THEME = SCENARIO_THEMES[0]

START_PLAYER = (0, 0)
WALLS = set()
EXIT = (9, 9)

LEVELS = {
    "easy": {
        "name": "EASY",
        "seconds": 45,
        "wall_count": 12,
        "enemy_start": (9, 0),
        "accent": EASY_COLOR,
        "description": "More time, open routes",
    },
    "medium": {
        "name": "MEDIUM",
        "seconds": 35,
        "wall_count": 23,
        "enemy_start": (8, 0),
        "accent": MEDIUM_COLOR,
        "description": "A tighter maze, closer enemy",
    },
    "hard": {
        "name": "HARD",
        "seconds": 30,
        "wall_count": 32,
        "enemy_start": (7, 0),
        "accent": HARD_COLOR,
        "description": "Dense maze, little time",
    },
}

EXIT_OPTIONS = [(9, 9), (9, 8), (8, 9), (9, 7), (8, 8), (7, 9)]


def find_path_bfs(start, goal, walls=None):
    """Return the shortest walkable path from start to goal, including both."""
    blocked_cells = WALLS if walls is None else walls
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        row, column = current
        neighbors = [
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        ]

        for neighbor in neighbors:
            next_row, next_column = neighbor
            inside_grid = 0 <= next_row < GRID_SIZE and 0 <= next_column < GRID_SIZE
            if inside_grid and neighbor not in blocked_cells and neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    if goal not in came_from:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def generate_scenario(wall_count, enemy_start, previous_theme=None):
    """Create a fresh maze and choose a theme different from the last one."""
    previous_name = previous_theme["name"] if previous_theme else None
    available_themes = [
        theme for theme in SCENARIO_THEMES if theme["name"] != previous_name
    ]
    theme = random.choice(available_themes)
    exit_cell = random.choice(EXIT_OPTIONS)
    protected_cells = {START_PLAYER, enemy_start, exit_cell}
    candidates = [
        (row, column)
        for row in range(GRID_SIZE)
        for column in range(GRID_SIZE)
        if (row, column) not in protected_cells
    ]
    random.shuffle(candidates)
    walls = set()

    for cell in candidates:
        if len(walls) == wall_count:
            break

        walls.add(cell)
        player_route = find_path_bfs(START_PLAYER, exit_cell, walls)
        enemy_route = find_path_bfs(enemy_start, START_PLAYER, walls)

        # Reject a wall if it blocks a route or makes the maze unfairly long.
        if not player_route or len(player_route) > 29 or not enemy_route:
            walls.remove(cell)

    return walls, exit_cell, theme


def cell_center(cell):
    """Convert a (row, column) cell into its pixel center."""
    row, column = cell
    x = GRID_X + column * CELL_SIZE + CELL_SIZE // 2
    y = GRID_Y + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def draw_text(surface, font, text, color, position):
    """Draw text using a top-left position."""
    surface.blit(font.render(text, True, color), position)


def draw_centered(surface, font, text, color, center):
    """Draw text centered at a pixel position."""
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def create_fonts():
    """Create fonts once so the game loop can reuse them."""
    return {
        "title": pygame.font.SysFont("arial", 28, bold=True),
        "hero": pygame.font.SysFont("arial", 52, bold=True),
        "level": pygame.font.SysFont("arial", 24, bold=True),
        "end_title": pygame.font.SysFont("arial", 48, bold=True),
        "timer": pygame.font.SysFont("arial", 48, bold=True),
        "label": pygame.font.SysFont("arial", 15, bold=True),
        "body": pygame.font.SysFont("arial", 18),
        "small": pygame.font.SysFont("arial", 14),
    }
def create_zombie_sprite():
    """Build a small transparent pixel-art zombie without external files."""
    sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
    outline = (19, 35, 34)
    skin = (107, 181, 116)
    skin_light = (151, 211, 139)
    skin_dark = (62, 125, 79)
    shirt = (94, 112, 79)
    eye_white = (242, 236, 199)
    wound = (174, 73, 65)

    # Legs and arms form the silhouette behind the body.
    pygame.draw.rect(sprite, outline, (11, 30, 8, 9))
    pygame.draw.rect(sprite, outline, (22, 30, 8, 9))
    pygame.draw.rect(sprite, skin_dark, (12, 31, 6, 6))
    pygame.draw.rect(sprite, skin_dark, (23, 31, 6, 6))
    pygame.draw.rect(sprite, outline, (9, 37, 10, 3))
    pygame.draw.rect(sprite, outline, (22, 37, 10, 3))
    pygame.draw.rect(sprite, outline, (2, 24, 9, 9))
    pygame.draw.rect(sprite, outline, (29, 23, 9, 10))
    pygame.draw.rect(sprite, skin, (3, 25, 7, 7))
    pygame.draw.rect(sprite, skin, (30, 24, 7, 8))

    # Jacket and torn sleeves.
    pygame.draw.rect(sprite, outline, (7, 22, 27, 12))
    pygame.draw.rect(sprite, shirt, (10, 23, 21, 10))
    pygame.draw.rect(sprite, skin_dark, (16, 24, 3, 8))
    pygame.draw.rect(sprite, skin_dark, (25, 27, 4, 3))
    pygame.draw.rect(sprite, outline, (5, 30, 6, 3))
    pygame.draw.rect(sprite, outline, (30, 29, 6, 3))

    # Blocky head, uneven hair, eyes, and a jagged mouth.
    pygame.draw.rect(sprite, outline, (8, 2, 24, 22))
    pygame.draw.rect(sprite, skin, (10, 5, 20, 17))
    pygame.draw.rect(sprite, skin_light, (12, 6, 12, 5))
    pygame.draw.rect(sprite, outline, (8, 2, 8, 4))
    pygame.draw.rect(sprite, outline, (18, 1, 9, 3))
    pygame.draw.rect(sprite, skin_dark, (10, 3, 5, 3))
    pygame.draw.rect(sprite, skin_dark, (23, 4, 7, 2))
    pygame.draw.rect(sprite, skin_dark, (7, 10, 4, 7))
    pygame.draw.rect(sprite, skin, (8, 11, 3, 5))
    pygame.draw.rect(sprite, skin_dark, (30, 10, 4, 7))
    pygame.draw.rect(sprite, skin, (30, 11, 3, 5))
    pygame.draw.rect(sprite, outline, (12, 10, 7, 5))
    pygame.draw.rect(sprite, outline, (22, 10, 7, 5))
    pygame.draw.rect(sprite, eye_white, (14, 11, 3, 3))
    pygame.draw.rect(sprite, eye_white, (23, 11, 3, 3))
    pygame.draw.rect(sprite, outline, (15, 12, 2, 2))
    pygame.draw.rect(sprite, outline, (23, 12, 2, 2))
    pygame.draw.rect(sprite, wound, (19, 15, 3, 3))
    pygame.draw.rect(sprite, outline, (14, 18, 13, 3))
    pygame.draw.rect(sprite, eye_white, (16, 18, 3, 2))
    pygame.draw.rect(sprite, eye_white, (22, 18, 3, 2))

    return pygame.transform.scale(sprite, (44, 44))


def draw_menu(surface, fonts, selected_level, level_cards, start_button):
    """Draw the difficulty selection screen."""
    surface.fill(BACKGROUND)

    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(surface, (23, 38, 42), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(surface, (23, 38, 42), (0, y), (SCREEN_WIDTH, y), 1)

    pygame.draw.rect(surface, PANEL, pygame.Rect(40, 34, 900, 48), border_radius=6)
    pygame.draw.rect(surface, EASY_COLOR, pygame.Rect(40, 34, 5, 48), border_radius=3)
    draw_text(surface, fonts["label"], "AI PROJECT  /  BREADTH-FIRST SEARCH", MUTED_TEXT, (61, 50))
    draw_text(surface, fonts["small"], "PROCEDURAL CHASE  -  10 x 10", TEXT_COLOR, (690, 51))

    draw_text(surface, fonts["hero"], "AI ESCAPE GRID", TEXT_COLOR, (60, 116))
    draw_text(
        surface,
        fonts["body"],
        "A different maze every run. Reach the exit before the hunter finds you.",
        MUTED_TEXT,
        (64, 184),
    )
    draw_text(surface, fonts["label"], "CHOOSE YOUR DIFFICULTY", TEXT_COLOR, (64, 266))

    for index, level_key in enumerate(("easy", "medium", "hard")):
        card = level_cards[level_key]
        config = LEVELS[level_key]
        accent = config["accent"]
        selected = level_key == selected_level
        fill = (37, 57, 60) if selected else (25, 42, 46)
        pygame.draw.rect(surface, fill, card, border_radius=8)
        pygame.draw.rect(surface, accent if selected else GRID_COLOR, card, 2, border_radius=8)
        pygame.draw.rect(surface, accent, pygame.Rect(card.x + 1, card.y + 1, card.width - 2, 5), border_radius=3)

        draw_text(surface, fonts["small"], f"0{index + 1}  /  LEVEL", MUTED_TEXT, (card.x + 20, card.y + 22))
        draw_text(surface, fonts["level"], config["name"], accent, (card.x + 20, card.y + 50))
        draw_text(surface, fonts["small"], config["description"], TEXT_COLOR, (card.x + 20, card.y + 91))
        draw_text(
            surface,
            fonts["label"],
            f"{config['seconds']} SEC   /   {config['wall_count']} WALLS",
            MUTED_TEXT,
            (card.x + 20, card.y + 121),
        )

    pygame.draw.rect(surface, EASY_COLOR, start_button, border_radius=6)
    draw_centered(surface, fonts["body"], "START RUN  [ENTER]", BACKGROUND, start_button.center)
    draw_centered(
        surface,
        fonts["small"],
        "Click a level or press 1, 2, 3.  Esc quits.",
        MUTED_TEXT,
        (SCREEN_WIDTH // 2, 610),
    )


def draw_game(
    surface,
    fonts,
    player,
    enemy,
    seconds_left,
    state,
    level_key,
    scenario_number,
    new_scenario_button,
    menu_button,
    zombie_sprite,
    theme,
):
    """Draw the maze, characters, level information, and end screen."""
    surface.fill(theme["background"])
    config = LEVELS[level_key]
    accent = config["accent"]
    draw_text(surface, fonts["title"], "AI ESCAPE GRID", TEXT_COLOR, (30, 23))
    draw_text(
        surface,
        fonts["small"],
        f"{config['name']}  /  SCENARIO {scenario_number:02d}",
        accent,
        (343, 34),
    )

    board_rect = pygame.Rect(
        GRID_X - 4,
        GRID_Y - 4,
        GRID_SIZE * CELL_SIZE + 8,
        GRID_SIZE * CELL_SIZE + 8,
    )
    pygame.draw.rect(surface, theme["panel"], board_rect, border_radius=8)

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            cell = (row, column)
            tile = pygame.Rect(
                GRID_X + column * CELL_SIZE,
                GRID_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(surface, theme["floor"], tile)
            pygame.draw.rect(surface, theme["grid"], tile, 1)

            if cell in WALLS:
                wall = tile.inflate(-8, -8)
                pygame.draw.rect(surface, theme["wall"], wall, border_radius=5)
                pygame.draw.line(
                    surface,
                    theme["wall_highlight"],
                    (wall.x + 7, wall.y + 3),
                    (wall.right - 7, wall.y + 3),
                    2,
                )

    # Draw the exit first so the characters appear clearly above the tile.
    exit_x, exit_y = cell_center(EXIT)
    pygame.draw.circle(surface, EXIT_COLOR, (exit_x, exit_y), 19, 3)
    pygame.draw.circle(surface, EXIT_COLOR, (exit_x, exit_y), 5)

    enemy_x, enemy_y = cell_center(enemy)
    surface.blit(zombie_sprite, zombie_sprite.get_rect(center=(enemy_x, enemy_y)))

    player_x, player_y = cell_center(player)
    pygame.draw.circle(surface, PLAYER_COLOR, (player_x, player_y), 17)
    pygame.draw.circle(surface, (220, 255, 244), (player_x - 5, player_y - 5), 5)

    panel = pygame.Rect(640, 82, 310, 580)
    pygame.draw.rect(surface, theme["panel"], panel, border_radius=8)
    draw_text(surface, fonts["label"], "CURRENT LEVEL", MUTED_TEXT, (670, 105))
    draw_text(surface, fonts["level"], config["name"], accent, (670, 128))
    draw_text(surface, fonts["small"], f"SCENARIO {scenario_number:02d}", MUTED_TEXT, (817, 137))
    draw_text(surface, fonts["small"], theme["name"], theme["accent"], (670, 160))
    pygame.draw.line(surface, theme["grid"], (670, 181), (920, 181), 1)
    draw_text(surface, fonts["label"], "TIME REMAINING", MUTED_TEXT, (670, 194))
    timer_color = EXIT_COLOR if seconds_left > 8 else ENEMY_COLOR
    draw_text(surface, fonts["timer"], f"{seconds_left:02d}", timer_color, (670, 215))
    draw_text(surface, fonts["small"], "SECONDS", MUTED_TEXT, (748, 235))

    status_text = {
        "playing": "Find the exit",
        "win": "You escaped!",
        "caught": "The enemy caught you",
        "time_up": "Time ran out",
    }[state]
    status_color = PLAYER_COLOR if state == "win" else TEXT_COLOR
    draw_text(surface, fonts["label"], "STATUS", MUTED_TEXT, (670, 280))
    draw_text(surface, fonts["body"], status_text, status_color, (670, 307))

    pygame.draw.line(surface, theme["grid"], (670, 350), (920, 350), 1)
    draw_text(surface, fonts["label"], "CONTROLS", MUTED_TEXT, (670, 370))
    draw_text(surface, fonts["body"], "Move:  Arrows or WASD", TEXT_COLOR, (670, 398))
    draw_text(surface, fonts["small"], "BFS enemy moves after each step.", MUTED_TEXT, (670, 430))
    draw_text(surface, fonts["small"], "Walls block both characters.", MUTED_TEXT, (670, 452))

    pygame.draw.rect(surface, theme["button"], new_scenario_button, border_radius=6)
    draw_text(
        surface,
        fonts["small"],
        "NEW SCENARIO  [R]",
        TEXT_COLOR,
        (new_scenario_button.x + 72, new_scenario_button.y + 14),
    )
    pygame.draw.rect(surface, theme["button"], menu_button, border_radius=6)
    draw_text(
        surface,
        fonts["small"],
        "CHANGE DIFFICULTY  [M]",
        TEXT_COLOR,
        (menu_button.x + 49, menu_button.y + 14),
    )

    if state != "playing":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 16, 19, 175))
        surface.blit(overlay, (0, 0))

        messages = {
            "win": ("YOU WIN", PLAYER_COLOR, "You found the exit in time."),
            "caught": ("GAME OVER", ENEMY_COLOR, "The enemy caught you."),
            "time_up": ("TIME UP", EXIT_COLOR, "The countdown reached zero."),
        }
        title, color, subtitle = messages[state]
        center_x = SCREEN_WIDTH // 2
        draw_centered(surface, fonts["end_title"], title, color, (center_x, 284))
        draw_centered(surface, fonts["body"], subtitle, TEXT_COLOR, (center_x, 334))
        draw_centered(surface, fonts["small"], "Press R for a fresh maze or M to change level", MUTED_TEXT, (center_x, 370))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Escape Grid | Procedural BFS Chase")
    clock = pygame.time.Clock()
    fonts = create_fonts()
    zombie_sprite = create_zombie_sprite()
    selected_level = "medium"
    level_cards = {
        "easy": pygame.Rect(48, 312, 280, 164),
        "medium": pygame.Rect(350, 312, 280, 164),
        "hard": pygame.Rect(652, 312, 280, 164),
    }
    start_button = pygame.Rect(360, 520, 260, 56)
    new_scenario_button = pygame.Rect(670, 500, 250, 42)
    menu_button = pygame.Rect(670, 555, 250, 42)
    player = START_PLAYER
    enemy = LEVELS[selected_level]["enemy_start"]
    start_time = 0
    scenario_number = 0
    state = "menu"
    running = True

    def start_new_scenario():
        nonlocal player, enemy, start_time, scenario_number, state
        global WALLS, EXIT, SCENARIO_THEME

        config = LEVELS[selected_level]
        WALLS, EXIT, SCENARIO_THEME = generate_scenario(
            config["wall_count"], config["enemy_start"], SCENARIO_THEME
        )
        player = START_PLAYER
        enemy = config["enemy_start"]
        start_time = pygame.time.get_ticks()
        scenario_number += 1
        state = "playing"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for level_key, card in level_cards.items():
                        if card.collidepoint(event.pos):
                            selected_level = level_key
                    if start_button.collidepoint(event.pos):
                        start_new_scenario()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        selected_level = "easy"
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        selected_level = "medium"
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        selected_level = "hard"
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        start_new_scenario()

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if new_scenario_button.collidepoint(event.pos):
                        start_new_scenario()
                    elif menu_button.collidepoint(event.pos):
                        state = "menu"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        state = "menu"
                    elif event.key == pygame.K_r:
                        start_new_scenario()
                    elif state == "playing":
                        moves = {
                            pygame.K_UP: (-1, 0),
                            pygame.K_w: (-1, 0),
                            pygame.K_DOWN: (1, 0),
                            pygame.K_s: (1, 0),
                            pygame.K_LEFT: (0, -1),
                            pygame.K_a: (0, -1),
                            pygame.K_RIGHT: (0, 1),
                            pygame.K_d: (0, 1),
                        }

                        if event.key in moves:
                            row_change, column_change = moves[event.key]
                            next_player = (
                                player[0] + row_change,
                                player[1] + column_change,
                            )
                            inside_grid = (
                                0 <= next_player[0] < GRID_SIZE
                                and 0 <= next_player[1] < GRID_SIZE
                            )

                            if inside_grid and next_player not in WALLS:
                                player = next_player
                                if player == EXIT:
                                    state = "win"
                                else:
                                    # Recalculate BFS after every successful player move.
                                    path = find_path_bfs(enemy, player)
                                    if len(path) > 1:
                                        enemy = path[1]
                                    if enemy == player:
                                        state = "caught"

        seconds_left = LEVELS[selected_level]["seconds"]
        if state in ("playing", "win", "caught", "time_up"):
            elapsed = (pygame.time.get_ticks() - start_time) // 1000
            seconds_left = max(0, LEVELS[selected_level]["seconds"] - elapsed)
            if state == "playing" and seconds_left == 0:
                state = "time_up"

        if state == "menu":
            draw_menu(screen, fonts, selected_level, level_cards, start_button)
        else:
            draw_game(
                screen,
                fonts,
                player,
                enemy,
                seconds_left,
                state,
                selected_level,
                scenario_number,
                new_scenario_button,
                menu_button,
                zombie_sprite,
                SCENARIO_THEME,
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()