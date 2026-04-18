import pygame
import random

pygame.init()

# НАСТРОЙКИ 
WIDTH, HEIGHT = 500, 500
CELL = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


snake = [[100, 100], [90, 100], [80, 100]]  # тело змейки
direction = "RIGHT"

# 
score = 0
level = 1
speed = 7  # начальная скорость

# ЕДА 
def generate_food():
    
    while True:
        food = [
            random.randrange(0, WIDTH, CELL),
            random.randrange(0, HEIGHT, CELL)
        ]
        if food not in snake:
            return food

food = generate_food()


running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Управление
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"
            elif event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"
            elif event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"
            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"

    head = snake[0].copy()

    if direction == "UP":
        head[1] -= CELL
    elif direction == "DOWN":
        head[1] += CELL
    elif direction == "LEFT":
        head[0] -= CELL
    elif direction == "RIGHT":
        head[0] += CELL

    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        print("Game Over (wall)")
        running = False

    snake.insert(0, head)

    if head == food:
        score += 1
        food = generate_food()

        if score % 3 == 0:
            level += 1
            speed += 2  # увеличиваем скорость

    else:
        snake.pop()

    #ОТРИСОВКА
    screen.fill(BLACK)

    # змейка
    for block in snake:
        pygame.draw.rect(screen, GREEN, (*block, CELL, CELL))

    # еда
    pygame.draw.rect(screen, RED, (*food, CELL, CELL))

    # заголовок (счёт и уровень)
    pygame.display.set_caption(f"Score: {score} | Level: {level}")

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()