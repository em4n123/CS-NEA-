import pygame
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('S.T.A.L.K.E.R 3')

#Player Setup

character = pygame.image.load('renegademan.png').convert_alpha()
width, height = character.get_size()
image = pygame.transform.scale(character, (width // 3, height // 3.5)) #png size scale
image_rect = image.get_rect(topleft=(1, 1))                          #sets spawn location

keys = {'w': False, 'a': False, 's': False, 'd': False}    #sets keys to false as default
speed = 1                                                   #speed of character png
running = True                                              #running = true as default (game is running)

#Maze Setup

Cell_Size = 90                              
Row_Size = 15                                  
Column_Size = 20                                   

class Cell:                                    #represents one square in the maze
    def __init__(self):                         
        self.visited = False                   
        self.walls = [True, True, True, True]  # top, right, bottom, left --- all walls exist by default

maze = [[Cell() for _ in range(Column_Size)] for _ in range(Row_Size)]    #creates 2D list/grid

def generate_maze(r, c):
    maze[r][c].visited = True                  #makrs current cells as visited - avoids infinite loops

    directions = [
        (0, -1, 0, 2),   # up
        (1, 0, 1, 3),    # right
        (0, 1, 2, 0),    # down
        (-1, 0, 3, 1)    # left
    ]

    random.shuffle(directions)                #makes a different maze each time the game is reset

    for dx, dy, wall, opposite in directions:
        nr, nc = r + dy, c + dx
        if 0 <= nr < Row_Size and 0 <= nc < Column_Size:          #boundary checking
            if not maze[nr][nc].visited:                #checks if neighbour cell is visited    (DFS)
                maze[r][c].walls[wall] = False          #removes wall of current cell
                maze[nr][nc].walls[opposite] = False    #removes wall of neighbour cell
                generate_maze(nr, nc)                   #Repeats process from neighbour cell

generate_maze(0, 0)                                     #starts maze generation from top left cell

def draw_maze():
    for r in range(Row_Size):
        for c in range(Column_Size):
            x = c * Cell_Size
            y = r * Cell_Size

            if maze[r][c].walls[0]:
                pygame.draw.line(screen, (0, 0, 0), (x, y), (x + Cell_Size, y), 2)
            if maze[r][c].walls[1]:
                pygame.draw.line(screen, (0, 0, 0), (x + Cell_Size, y), (x + Cell_Size, y + Cell_Size), 2)
            if maze[r][c].walls[2]:
                pygame.draw.line(screen, (0, 0, 0), (x, y + Cell_Size), (x + Cell_Size, y + Cell_Size), 2)
            if maze[r][c].walls[3]:
                pygame.draw.line(screen, (0, 0, 0), (x, y), (x, y + Cell_Size), 2)

#Main Game Loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:                                        #sets wasd keys to true when pressed                     
            if event.key == pygame.K_F11:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)      #set to fullscreen via F11
            elif event.key == pygame.K_ESCAPE:                                   #set to windowed via esc
                screen = pygame.display.set_mode((800, 600))
            elif event.key == pygame.K_w:                   
                keys['w'] = True
            elif event.key == pygame.K_a:
                keys['a'] = True
            elif event.key == pygame.K_s:
                keys['s'] = True
            elif event.key == pygame.K_d:
                keys['d'] = True

        if event.type == pygame.KEYUP:      #sets keys wasd false when keys not pressed
            if event.key == pygame.K_w:
                keys['w'] = False
            elif event.key == pygame.K_a:
                keys['a'] = False
            elif event.key == pygame.K_s:
                keys['s'] = False
            elif event.key == pygame.K_d:
                keys['d'] = False

    if keys['w']:
        image_rect.y -= speed                #y axis Negative speed if w is true
    if keys['s']:
        image_rect.y += speed                #y axis Positive speed if s is true
    if keys['a']:
        image_rect.x -= speed                #x axis Negative speed if a is true
    if keys['d']:
        image_rect.x += speed                #x axis Positive speed if d is true

    screen.fill((255, 255, 255))                  #clears screen
    draw_maze()                              #draws randomly generated maze
    screen.blit(image, image_rect)          #places png in new position before displaying it
    pygame.display.flip()                   #shows new png position
                                            #(done every frame)

pygame.quit()
