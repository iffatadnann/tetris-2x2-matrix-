import pygame
import random
import numpy as np  # For matrix operations (linear algebra)

colors = [
    (255, 102, 204),
    (0, 51, 204),
    (0, 204, 0),
    (255, 102, 0),
    (204, 51, 255),
    (153, 0, 51),
    (0, 204, 255)
]

# Tetrominoes defined using (x, y) vectors relative to a top-left origin
tetromino_shapes = [
    [[(0, 0), (1, 0), (0, 1), (1, 1)]],  # O
    [[(0, 0), (0, 1), (1, 1), (1, 2)]],  # Z
    [[(0, 1), (1, 1), (1, 0), (2, 0)]],  # S
    [[(0, 0), (1, 0), (1, 1), (1, 2)]],  # L
    [[(0, 2), (1, 0), (1, 1), (1, 2)]],  # J
    [[(0, 1), (1, 0), (1, 1), (2, 1)]],  # T
    [[(0, 0), (1, 0), (2, 0), (3, 0)]],  # I
]

def rotate_point_90(x, y):
    # 90-degree counter-clockwise rotation using a rotation matrix
    # [0 -1]
    # [1  0]
    return -y, x

class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(tetromino_shapes) - 1)
        self.color = random.randint(0, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return tetromino_shapes[self.type][0]

    def rotated_image(self):
        rotated = [rotate_point_90(x, y) for (x, y) in self.image()]
        min_x = min(p[0] for p in rotated)
        min_y = min(p[1] for p in rotated)
        return [(x - min_x, y - min_y) for (x, y) in rotated]

    def rotate(self):
        tetromino_shapes[self.type][0] = self.rotated_image()

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = [[0 for _ in range(width)] for _ in range(height)]
        self.figure = None
        self.level = 2
        self.score = 0
        self.state = "start"

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self):
        # Checks boundary + filled cell collisions using vector geometry
        for x, y in self.figure.image():
            px = self.figure.x + x
            py = self.figure.y + y
            if px < 0 or px >= self.width or py >= self.height or self.field[py][px]:
                return True
        return False

    def freeze(self):
        for x, y in self.figure.image():
            self.field[self.figure.y + y][self.figure.x + x] = self.figure.color + 1
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def break_lines(self):
        # Performs row deletion and matrix-style shifting using list operations
        lines = 0
        new_field = [row for row in self.field if any(cell == 0 for cell in row)]
        lines = self.height - len(new_field)
        for _ in range(lines):
            new_field.insert(0, [0 for _ in range(self.width)])
        self.field = new_field
        self.score += lines ** 2

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def go_side(self, dx):
        self.figure.x += dx
        if self.intersects():
            self.figure.x -= dx

    def rotate(self):
        old = self.figure.image()[:]
        self.figure.rotate()
        if self.intersects():
            tetromino_shapes[self.figure.type][0] = old

# ----- Game Loop with ORIGINAL DISPLAY ----- #
pygame.init()
screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Tetris")
done = False
clock = pygame.time.Clock()
game = Tetris(20, 10)
fps = 25
counter = 0
pressing_down = False

while not done:
    if game.figure is None:
        game.new_figure()

    counter += 1
    if counter > 10000:
        counter = 0

    if counter % (fps // game.level) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                game.go_side(-1)
            if event.key == pygame.K_RIGHT:
                game.go_side(1)
            if event.key == pygame.K_SPACE:
                while not game.intersects():
                    game.figure.y += 1
                game.figure.y -= 1
                game.freeze()
            if event.key == pygame.K_ESCAPE:
                game.__init__(20, 10)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                pressing_down = False

    screen.fill((0,0,0))
    for y in range(game.height):
        for x in range(game.width):
            pygame.draw.rect(screen, (255,0,255), [20 + 20 * x, 20 + 20 * y, 20, 20], 1)
            if game.field[y][x]:
                pygame.draw.rect(screen, colors[game.field[y][x] - 1],
                                 [21 + 20 * x, 21 + 20 * y, 18, 18])

    if game.figure:
        for x, y in game.figure.image():
            pygame.draw.rect(screen, colors[game.figure.color],
                             [21 + 20 * (game.figure.x + x), 21 + 20 * (game.figure.y + y), 18, 18])

    font = pygame.font.SysFont('Calibri', 25, True, False)
    text = font.render("Score: " + str(game.score), True, (255,255,255))
    screen.blit(text, [0, 0])

    if game.state == "gameover":
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        screen.blit(font1.render("Game Over", True, (255, 0, 0)), [40, 200])
        screen.blit(font1.render("Press ESC", True, (255, 255, 0)), [50, 270])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
