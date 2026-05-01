

import pygame
import random
import json
from config import *

def load_settings():
    with open("settings.json") as f:
        return json.load(f)

def save_settings(s):
    with open("settings.json", "w") as f:
        json.dump(s, f)

class Game:
    def __init__(self, screen, pid, best):
        self.screen = screen
        self.pid = pid
        self.best = best
        self.font = pygame.font.SysFont(None, 26)
        self.settings = load_settings()  # load once, not every frame
        self.reset()

    def reset(self):
        self.snake = [(COLS // 2, ROWS // 2)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.level = 1
        self.eaten = 0
        self.speed = 8
        self.over = False

        self.obstacles = []
        self.foods = []
        self.powerup = None        # [x, y, type, spawn_time]
        self.active_pu = None      # current active powerup type
        self.pu_end = 0            # when active powerup ends
        self.shield = False

        self.spawn_food()

    def free_cell(self):
        # find a random cell not occupied by anything
        taken = set(self.snake) | set(self.obstacles)
        for f in self.foods:
            taken.add((f[0], f[1]))
        if self.powerup:
            taken.add((self.powerup[0], self.powerup[1]))
        for _ in range(500):
            x = random.randint(1, COLS - 2)
            y = random.randint(1, ROWS - 2)
            if (x, y) not in taken:
                return x, y
        return None

    def spawn_food(self):
        pos = self.free_cell()
        if not pos:
            return
        x, y = pos
        r = random.random()
        if r < 0.15:
            ftype, pts = 'poison', 0
        elif r < 0.4:
            ftype, pts = 'heavy', 3
        else:
            ftype, pts = 'normal', 1
        self.foods.append([x, y, ftype, pts, pygame.time.get_ticks()])

    def spawn_powerup(self):
        pos = self.free_cell()
        if not pos:
            return
        x, y = pos
        ptype = random.choice(['speed', 'slow', 'shield'])
        self.powerup = [x, y, ptype, pygame.time.get_ticks()]

    def spawn_obstacles(self):
        self.obstacles = []
        hx, hy = self.snake[0]
        taken = set(self.snake)
        count = 3 + self.level
        for _ in range(500):
            if len(self.obstacles) >= count:
                break
            x = random.randint(1, COLS - 2)
            y = random.randint(1, ROWS - 2)
            # keep area around snake head clear
            if abs(x - hx) < 4 and abs(y - hy) < 4:
                continue
            if (x, y) not in taken:
                self.obstacles.append((x, y))
                taken.add((x, y))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.dir != (0, 1):
                self.next_dir = (0, -1)
            elif event.key == pygame.K_DOWN and self.dir != (0, -1):
                self.next_dir = (0, 1)
            elif event.key == pygame.K_LEFT and self.dir != (1, 0):
                self.next_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.dir != (-1, 0):
                self.next_dir = (1, 0)

    def update(self):
        now = pygame.time.get_ticks()
        if now - getattr(self, 'last_move', 0) < 1000 // self.speed:
            return
        self.last_move = now

        self.dir = self.next_dir
        hx, hy = self.snake[0]
        dx, dy = self.dir
        nx, ny = hx + dx, hy + dy

        # wall collision
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            if self.shield:
                nx, ny = nx % COLS, ny % ROWS
                self.shield = False
                self.active_pu = None
            else:
                self.over = True
                return

        # obstacle collision
        if (nx, ny) in self.obstacles:
            if self.shield:
                self.shield = False
                self.active_pu = None
            else:
                self.over = True
                return

        # self collision
        if (nx, ny) in self.snake:
            if self.shield:
                self.shield = False
                self.active_pu = None
            else:
                self.over = True
                return

        self.snake.insert(0, (nx, ny))
        grew = False

        # check food
        for f in self.foods[:]:
            if (f[0], f[1]) == (nx, ny):
                if f[2] == 'poison':
                    # shorten by 2
                    for _ in range(2):
                        if len(self.snake) > 1:
                            self.snake.pop()
                    if len(self.snake) <= 1:
                        self.over = True
                        return
                else:
                    self.score += f[3]
                    self.eaten += 1
                    grew = True
                self.foods.remove(f)
                self.spawn_food()
                # level up every 5 foods
                if self.eaten % 5 == 0:
                    self.level += 1
                    self.speed = min(20, self.speed + 1)
                    if self.level >= 3:
                        self.spawn_obstacles()
                break

        if not grew:
            self.snake.pop()

        # check powerup pickup
        if self.powerup and (self.powerup[0], self.powerup[1]) == (nx, ny):
            pt = self.powerup[2]
            self.active_pu = pt
            if pt == 'speed':
                self.speed += 4
                self.pu_end = now + 5000
            elif pt == 'slow':
                self.speed = max(3, self.speed - 4)
                self.pu_end = now + 5000
            elif pt == 'shield':
                self.shield = True
            self.powerup = None

        # end timed powerups
        if self.active_pu in ('speed', 'slow') and now > self.pu_end:
            if self.active_pu == 'speed':
                self.speed -= 4
            else:
                self.speed += 4
            self.active_pu = None

        # remove old food after 10 sec
        for f in self.foods[:]:
            if now - f[4] > 10000:
                self.foods.remove(f)
                self.spawn_food()

        # remove old powerup after 8 sec
        if self.powerup and now - self.powerup[3] > 8000:
            self.powerup = None

        # randomly spawn powerup
        if not self.powerup and random.random() < 0.005:
            self.spawn_powerup()

    def draw(self):
        s = self.settings
        self.screen.fill(BLACK)

        # obstacles
        for ox, oy in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, (ox*CELL, oy*CELL, CELL, CELL))

        # food
        color_map = {'normal': RED, 'heavy': ORANGE, 'poison': DARK_RED}
        for f in self.foods:
            c = color_map[f[2]]
            pygame.draw.rect(self.screen, c, (f[0]*CELL+2, f[1]*CELL+2, CELL-4, CELL-4))

        # powerup
        if self.powerup:
            pu_colors = {'speed': YELLOW, 'slow': BLUE, 'shield': PURPLE}
            c = pu_colors[self.powerup[2]]
            pygame.draw.rect(self.screen, c, (self.powerup[0]*CELL+2, self.powerup[1]*CELL+2, CELL-4, CELL-4))

        # snake
        sc = tuple(s.get('snake_color', [0, 200, 0]))
        for i, (x, y) in enumerate(self.snake):
            c = WHITE if i == 0 else sc
            pygame.draw.rect(self.screen, c, (x*CELL, y*CELL, CELL, CELL))

        # hud
        txt = self.font.render(f"Score:{self.score}  Level:{self.level}  Best:{self.best}", True, WHITE)
        self.screen.blit(txt, (5, 5))
        if self.active_pu:
            pt = self.font.render(f"Powerup: {self.active_pu}", True, YELLOW)
            self.screen.blit(pt, (5, 25))
        if self.shield:
            sh = self.font.render("SHIELD", True, PURPLE)
            self.screen.blit(sh, (WIDTH - 70, 5))