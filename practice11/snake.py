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
YELLOW = (255, 255, 0)   
ORANGE = (255, 165, 0)  

snake = [[100, 100], [90, 100], [80, 100]]  
direction = "RIGHT"

score = 0
level = 1
speed = 7  

# ДОБАВЛЕНО: переменные для еды с весом и таймером
food = None
food_weight = 1           
food_timer = 0            
FOOD_LIFETIME = 150       

# ЕДА (НОВАЯ ВЕРСИЯ)
def generate_food():
    global food_weight, food_timer
    
    while True:
        food_pos = [
            random.randrange(0, WIDTH, CELL),
            random.randrange(0, HEIGHT, CELL)
        ]
        if food_pos not in snake:
            # РАЗНЫЕ ВЕСА: случайный выбор веса еды
            # 60% - вес 1 (красный), 30% - вес 2 (оранжевый), 10% - вес 3 (желтый)
            rand = random.random()
            if rand < 0.6:
                food_weight = 1     
            elif rand < 0.9:
                food_weight = 2    
            else:
                food_weight = 3      
            
            food_timer = FOOD_LIFETIME  
            return food_pos

# Генерируем первую еду
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

    # ДОБАВЛЕНО: проверка с учётом веса еды
    if head == food:
        score += food_weight       
        food = generate_food()       

        if score % 3 == 0:
            level += 1
            speed += 2 

    else:
        snake.pop()

    # ДОБАВЛЕНО: уменьшаем таймер еды
    if food_timer > 0:
        food_timer -= 1
        if food_timer <= 0:
            food = generate_food()  

    screen.fill(BLACK)

    for block in snake:
        pygame.draw.rect(screen, GREEN, (*block, CELL, CELL))

    if food_weight == 1:
        food_color = RED        # вес 1 - красный
    elif food_weight == 2:
        food_color = ORANGE     # вес 2 - оранжевый
    else:
        food_color = YELLOW     # вес 3 - желтый
    
    pygame.draw.rect(screen, food_color, (*food, CELL, CELL))

    pygame.display.set_caption(f"Score: {score} | Level: {level} | Food weight: {food_weight}")

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()