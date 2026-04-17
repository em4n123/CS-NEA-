import pygame
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('S.T.A.L.K.E.R 3')

completion_time = None     # stores how long the user took
leaderboard = []           # holds all the scores in memory
LEADERBOARD_FILE = "leaderboard.txt"
difficulty = "Medium"      # default difficulty setting

# Difficulty Settings (changes cell size to increase maze size)
DIFFICULTY_SETTINGS = {
    "Easy":   120,          # fewer and larger cells = simpler maze
    "Medium": 90,           # default cell size
    "Hard":   60            # more and smaller cells = complex maze
}

# Player Class
class Player:
    def __init__(self, start_x, start_y):
        self.character = pygame.image.load('renegademan.png').convert_alpha()
        width, height = self.character.get_size()
        self.image = pygame.transform.scale(self.character, (width // 3, int(height // 3.5)))  # png size (scale)
        self.rect = self.image.get_rect(center=(start_x, start_y))   # sets spawn location
        self.speed = 2                                                 # speed of character png
        self.keys = {'w': False, 'a': False, 's': False, 'd': False}  # sets keys to false as default
        self.start_time = None                                         # records when player touches w, a, s or d

    def handle_keydown(self, key):                 # sets movement keys to true once user presses w, a, s or d
        if key == pygame.K_w:
            self.keys['w'] = True
        elif key == pygame.K_a:
            self.keys['a'] = True
        elif key == pygame.K_s:
            self.keys['s'] = True
        elif key == pygame.K_d:
            self.keys['d'] = True

    def handle_keyup(self, key):                   # sets movement keys to false when no keys are pressed
        if key == pygame.K_w:
            self.keys['w'] = False
        elif key == pygame.K_a:
            self.keys['a'] = False
        elif key == pygame.K_s:
            self.keys['s'] = False
        elif key == pygame.K_d:
            self.keys['d'] = False

    def get_movement(self):                        # returns dx, dy based on keys pressed
        dx = dy = 0
        if self.keys['w']:
            dy -= self.speed                       # y axis Negative speed if w is true
        if self.keys['s']:
            dy += self.speed                       # y axis Positive speed if s is true
        if self.keys['a']:
            dx -= self.speed                       # x axis Negative speed if a is true
        if self.keys['d']:
            dx += self.speed                       # x axis Positive speed if d is true
        return dx, dy

    def move_and_collide(self, dx, dy, wall_rects):
        self.rect.x += dx                          # move horizontally
        for wall in wall_rects:                    # cancel movement if hitting wall
            if self.rect.colliderect(wall):
                self.rect.x -= dx
                break
        self.rect.y += dy                          # move vertically
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                self.rect.y -= dy
                break

    def draw(self, surface):                       # draws player png to screen
        surface.blit(self.image, self.rect)

    def reset(self, cell_size):                    # resets player to spawn and restarts timer
        self.rect.center = (cell_size // 2, cell_size // 2)
        self.start_time = pygame.time.get_ticks()  # resets timer for new game

    def start_timer(self):                         # starts the timer
        self.start_time = pygame.time.get_ticks()

    def get_elapsed_time(self):                    # returns recorded time in seconds
        return (pygame.time.get_ticks() - self.start_time) / 1000


# Maze Setup

Cell_Size = DIFFICULTY_SETTINGS[difficulty]        # cell size set by difficulty

# Calculate maze size based on screen size
Row_Size = screen.get_height() // Cell_Size
Column_Size = screen.get_width() // Cell_Size

# Start and Finish cells (top-left and bottom-right corners)
start_cell = (0, 0)
finish_cell = (Row_Size - 1, Column_Size - 1)      # Uses actual maze size

class Cell:                                        # represents one square in the maze
    def __init__(self):
        self.visited = False
        self.walls = [True, True, True, True]      # top, right, bottom, left

maze = [[Cell() for _ in range(Column_Size)] for _ in range(Row_Size)]    # creates 2D list/grid

def generate_maze(r, c):
    maze[r][c].visited = True                      # marks current cell as visited

    directions = [
        (0, -1, 0, 2),   # up
        (1, 0, 1, 3),    # right
        (0, 1, 2, 0),    # down
        (-1, 0, 3, 1)    # left
    ]

    random.shuffle(directions)                     # makes a different maze each time

    for dx, dy, wall, opposite in directions:
        nr, nc = r + dy, c + dx
        if 0 <= nr < Row_Size and 0 <= nc < Column_Size:      # boundary checking
            if not maze[nr][nc].visited:                       # DFS
                maze[r][c].walls[wall] = False                 # remove wall
                maze[nr][nc].walls[opposite] = False
                generate_maze(nr, nc)

generate_maze(0, 0)                                # starts maze generation

wall_rects = []                                    # stores wall collision boxes

def draw_maze():
    wall_rects.clear()                             # clears old walls each frame
    for r in range(Row_Size):
        for c in range(Column_Size):
            x = c * Cell_Size
            y = r * Cell_Size

            if maze[r][c].walls[0]:                # top wall
                rect = pygame.Rect(x, y, Cell_Size, 2)
                wall_rects.append(rect)
                pygame.draw.rect(screen, (0, 0, 0), rect)

            if maze[r][c].walls[1]:                # right wall
                rect = pygame.Rect(x + Cell_Size, y, 2, Cell_Size)
                wall_rects.append(rect)
                pygame.draw.rect(screen, (0, 0, 0), rect)

            if maze[r][c].walls[2]:                # bottom wall
                rect = pygame.Rect(x, y + Cell_Size, Cell_Size, 2)
                wall_rects.append(rect)
                pygame.draw.rect(screen, (0, 0, 0), rect)

            if maze[r][c].walls[3]:                # left wall
                rect = pygame.Rect(x, y, 2, Cell_Size)
                wall_rects.append(rect)
                pygame.draw.rect(screen, (0, 0, 0), rect)

# gets rectangle for a maze cell (used for start and finish zones)
def get_cell_rect(r, c):
    x = c * Cell_Size
    y = r * Cell_Size
    return pygame.Rect(x + 10, y + 10, Cell_Size - 20, Cell_Size - 20)

# creates start and finish rectangles
start_rect = get_cell_rect(*start_cell)
finish_rect = get_cell_rect(*finish_cell)

def rebuild_maze():
    # rebuilds maze size and regenerates when difficulty changes
    global Row_Size, Column_Size, maze, start_rect, finish_rect, finish_cell, Cell_Size
    Cell_Size = DIFFICULTY_SETTINGS[difficulty]
    Row_Size = screen.get_height() // Cell_Size
    Column_Size = screen.get_width() // Cell_Size
    finish_cell = (Row_Size - 1, Column_Size - 1)
    maze = [[Cell() for _ in range(Column_Size)] for _ in range(Row_Size)]
    generate_maze(0, 0)
    start_rect = get_cell_rect(*start_cell)
    finish_rect = get_cell_rect(*finish_cell)

def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            for line in f:
                try:
                    parts = line.strip().split(",")
                    if len(parts) == 3:                                        # format: name, time, difficulty
                        leaderboard.append((parts[0], float(parts[1]), parts[2]))
                    elif len(parts) == 1:                                      
                        leaderboard.append(("Unknown", float(parts[0]), "Medium"))
                except ValueError:
                    pass                                                       # skip error lines (e.g if time isnt a float)
        leaderboard.sort(key=lambda x: x[1])      # best times first (lowest time)
    except FileNotFoundError:
        pass                                       # no file yet start fresh

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        for entry in leaderboard:
            f.write(f"{entry[0]},{entry[1]},{entry[2]}\n")  # saves name, time, difficulty

load_leaderboard()                                 # loads existing scores when game launches

# Player Setup (after class is defined)
player = Player(Cell_Size // 2, Cell_Size // 2)    # spawns player in centre of first cell

running = True                                     # running = true as default (game is running)
game_state = "menu"                                # starts on menu screen
player_name = ""                                   # stores typed name on win screen
entering_name = True                               # tracks if player is still typing name

# Menu Screen
def draw_menu():
    screen.fill((20, 20, 20))                      # dark background for menu
    font_title = pygame.font.SysFont('Arial', 80, bold=True)
    font_option = pygame.font.SysFont('Arial', 40)
    font_diff = pygame.font.SysFont('Arial', 35)

    title = font_title.render('S.T.A.L.K.E.R 3', True, (200, 150, 0))       # orange/gold title text
    start_text = font_option.render('Press ENTER to Start', True, (255, 255, 255))
    quit_text = font_option.render('Press ESC to Quit', True, (180, 180, 180))
    diff_label = font_diff.render(f'Difficulty: {difficulty}  (LEFT / RIGHT to change)', True, (180, 180, 180))

    # centres each piece of text on screen
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3)))
    screen.blit(start_text, start_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
    screen.blit(quit_text, quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60)))
    screen.blit(diff_label, diff_label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 130)))

# Win Screen
def draw_win():
    screen.fill((20, 20, 20))                      # dark background for win screen
    font_win = pygame.font.SysFont('Arial', 60, bold=True)
    font_sub = pygame.font.SysFont('Arial', 35)
    font_lb = pygame.font.SysFont('Arial', 28)

    win_text = font_win.render('Maze Completed!', True, (0, 220, 0))         # green win message
    time_text = font_sub.render(f'Your time: {completion_time:.2f}s  [{difficulty}]', True, (255, 215, 0))

    # centres each piece of text on screen
    screen.blit(win_text, win_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 8)))
    screen.blit(time_text, time_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 8 + 80)))

    if entering_name:                              # shows name entry prompt if still typing
        prompt = font_sub.render('Enter your name: ' + player_name + '|', True, (255, 255, 255))
        hint = font_lb.render('Press ENTER to save', True, (180, 180, 180))
        screen.blit(prompt, prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20)))
        screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40)))
    else:
        # draws leaderboard title
        lb_title = font_sub.render('Top 5 Times:', True, (200, 150, 0))
        screen.blit(lb_title, lb_title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40)))

        for i, entry in enumerate(leaderboard[:5]):           # shows top 5 only
            colour = (255, 215, 0) if entry[0] == player_name and entry[1] == completion_time else (255, 255, 255)  # highlights your score
            row = font_lb.render(f'{i+1}. {entry[0]}  {entry[1]:.2f}s  [{entry[2]}]', True, colour)
            screen.blit(row, row.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + (i * 40))))

        sub_text = font_sub.render('Press ENTER to play again or ESC to quit', True, (255, 255, 255))
        screen.blit(sub_text, sub_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80)))

# Main Game Loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == "menu":                                            # menu screen key handling
                if event.key == pygame.K_RETURN:                               # Enter key starts the game
                    rebuild_maze()                                              # rebuilds maze for selected difficulty
                    player.reset(Cell_Size)                                    # resets player position and starts timer
                    game_state = "playing"
                elif event.key == pygame.K_ESCAPE:                             # ESC key quits from menu
                    running = False
                elif event.key == pygame.K_LEFT:                               # Left arrow key cycles difficulty down
                    keys_list = list(DIFFICULTY_SETTINGS.keys())
                    difficulty = keys_list[(keys_list.index(difficulty) - 1) % len(keys_list)]
                elif event.key == pygame.K_RIGHT:                              # Right arrow key cycles difficulty up
                    keys_list = list(DIFFICULTY_SETTINGS.keys())
                    difficulty = keys_list[(keys_list.index(difficulty) + 1) % len(keys_list)]

            elif game_state == "playing":                                       # in-game key handling
                if event.key == pygame.K_F11:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)     # set to fullscreen via F11
                elif event.key == pygame.K_ESCAPE:                                  # set to windowed via esc
                    screen = pygame.display.set_mode((800, 600))
                else:
                    player.handle_keydown(event.key)                           # passes keypress to player class

            elif game_state == "win":                                           # win screen key handling
                if entering_name:                                               # handle name typing
                    if event.key == pygame.K_RETURN and player_name.strip():   # Enter key saves name if prompt is not empty
                        leaderboard.append((player_name.strip(), completion_time, difficulty))
                        leaderboard.sort(key=lambda x: x[1])                  # sorts leaderboard (best first)
                        save_leaderboard()                                     # saves leaderboard to file
                        entering_name = False                                  # switches to leaderboard view
                    elif event.key == pygame.K_BACKSPACE:                      # Backspace key deletes last character entered by user
                        player_name = player_name[:-1]
                    elif len(player_name) < 12:                                # caps name at 12 characters
                        player_name += event.unicode                           # adds typed character to name
                else:
                    if event.key == pygame.K_RETURN:                           # Enter key regenerates maze and restarts
                        rebuild_maze()                                         # generates a fresh maze
                        player.reset(Cell_Size)                                # resets player to spawn
                        player_name = ""                                       # clears name for next run
                        entering_name = True                                   # re-enables name entry
                        game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:                         # ESC key quits from win screen
                        running = False

        if event.type == pygame.KEYUP and game_state == "playing":             # sets keys wasd false when released
            player.handle_keyup(event.key)

    if game_state == "menu":                # shows menu screen
        draw_menu()

    elif game_state == "playing":           # main gameplay

        dx, dy = player.get_movement()      # gets movement from player class

        screen.fill((255, 255, 255))        # clears screen
        draw_maze()                         # draws randomly generated maze

        # draws start (green) and finish (red)
        pygame.draw.rect(screen, (0, 200, 0), start_rect)
        pygame.draw.rect(screen, (200, 0, 0), finish_rect)

        player.move_and_collide(dx, dy, wall_rects)   # moves player with wall collision
        player.draw(screen)                            # places png in new position

        # checks if player has reached the finish
        if player.rect.colliderect(finish_rect):
            completion_time = player.get_elapsed_time()    # calculates time in seconds
            entering_name = True                           # prompts name entry on win screen
            player_name = ""                               # clears name ready for input
            game_state = "win"                             # switches to win screen

    elif game_state == "win":               # shows win screen
        draw_win()

    pygame.display.flip()                  # shows new png position (done every frame)

pygame.quit()
