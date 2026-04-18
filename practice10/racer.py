import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ЗАГРУЗКА КАРТИНОК 
background = pygame.image.load('resour/road.png')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_img = pygame.image.load("resour/player.png")
player_img = pygame.transform.scale(player_img, (60, 80))

enemy_img = pygame.image.load("resour/Enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (60, 80))

coin_img = pygame.image.load("resour/coin2.png")
coin_img = pygame.transform.scale(coin_img, (40, 40))

#  ПЕРЕМЕННЫЕ 
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 5

enemy_x = random.randint(50, WIDTH - 100)
enemy_y = -100
enemy_speed = 5

coin_x = random.randint(50, WIDTH - 100)
coin_y = -50

score = 0
font = pygame.font.SysFont("Arial", 24)

#  ИГРОВОЙ ЦИКЛ 
running = True
while running:

    # события
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # управление
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # движение врага
    enemy_y += enemy_speed
    if enemy_y > HEIGHT:
        enemy_y = -100
        enemy_x = random.randint(50, WIDTH - 100)

    # движение монеты
    coin_y += 4
    if coin_y > HEIGHT:
        coin_y = -50
        coin_x = random.randint(50, WIDTH - 100)

    # СТОЛКНОВЕНИЯ 

    player_rect = pygame.Rect(player_x, player_y, 60, 80)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, 60, 80)
    coin_rect = pygame.Rect(coin_x, coin_y, 40, 40)

    # столкновение с врагом
    if player_rect.colliderect(enemy_rect):
        print("Game Over")
        pygame.time.delay(2000)
        running = False

    # сбор монеты
    if player_rect.colliderect(coin_rect):
        score += 1
        coin_y = -50
        coin_x = random.randint(50, WIDTH - 100)

    #  ОТРИСОВКА 
    screen.blit(background, (0, 0))
    screen.blit(player_img, (player_x, player_y))
    screen.blit(enemy_img, (enemy_x, enemy_y))
    screen.blit(coin_img, (coin_x, coin_y))

    # счёт (правый верх)
    text = font.render(f"Coins: {score}", True, (0, 0, 0))
    screen.blit(text, (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()