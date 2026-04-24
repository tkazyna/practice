import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ЗАГРУЗКА КАРТИНОК 
background = pygame.image.load("resour/road.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_img = pygame.image.load("resour/player.png")
player_img = pygame.transform.scale(player_img, (60, 80))

enemy_img = pygame.image.load("resour/Enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (60, 80))

coin_img = pygame.image.load("resour/coin2.png")
coin_img = pygame.transform.scale(coin_img, (40, 40))

# ДОБАВЛЕНО: загрузка золотой монеты для веса 2
gold_coin_img = pygame.image.load("resour/coin2.png")
gold_coin_img = pygame.transform.scale(gold_coin_img, (40, 40))
# (можно использовать ту же картинку или создать золотую)

#  ПЕРЕМЕННЫЕ 
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 5

enemy_x = random.randint(50, WIDTH - 100)
enemy_y = -100
enemy_speed = 5

# ДОБАВЛЕНО: переменные для монет с весом
coin_x = random.randint(50, WIDTH - 100)
coin_y = -50
coin_weight = 1  # вес монеты (1 или 2)

score = 0
N_COINS_FOR_SPEED_UP = 5  # через сколько монет увеличивается скорость врага
font = pygame.font.SysFont("Arial", 24)

# ДОБАВЛЕНО: функция генерации монеты со случайным весом
def generate_coin():
    global coin_x, coin_y, coin_weight
    coin_x = random.randint(50, WIDTH - 100)
    coin_y = -50
    # случайный вес: 70% - вес 1, 30% - вес 2
    if random.random() < 0.7:
        coin_weight = 1
    else:
        coin_weight = 2

# Генерируем первую монету
generate_coin()

#  ИГРОВОЙ ЦИКЛ 
running = True
while running:

    # события
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # управление с ограничением по краям
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 60:
        player_x += player_speed

    # движение врага
    enemy_y += enemy_speed
    if enemy_y > HEIGHT:
        enemy_y = -100
        enemy_x = random.randint(50, WIDTH - 100)

    # движение монеты
    coin_y += 4
    if coin_y > HEIGHT:
        generate_coin()  # используем новую функцию

    # СТОЛКНОВЕНИЯ 
    player_rect = pygame.Rect(player_x, player_y, 60, 80)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, 60, 80)
    coin_rect = pygame.Rect(coin_x, coin_y, 40, 40)

    # столкновение с врагом
    if player_rect.colliderect(enemy_rect):
        print("Game Over")
        pygame.time.delay(2000)
        running = False

    # ДОБАВЛЕНО: сбор монеты с учётом веса
    if player_rect.colliderect(coin_rect):
        score += coin_weight  # добавляем вес монеты (1 или 2)
        print(f"Collected coin! Weight: {coin_weight}, Total: {score}")
        
        # ДОБАВЛЕНО: увеличение скорости врага после N монет
        if score % N_COINS_FOR_SPEED_UP == 0 and score > 0:
            enemy_speed += 1
            print(f"Enemy speed increased! Now: {enemy_speed}")
        
        generate_coin()  

    #  ОТРИСОВКА 
    screen.blit(background, (0, 0))
    screen.blit(player_img, (player_x, player_y))
    screen.blit(enemy_img, (enemy_x, enemy_y))
    
    # ДОБАВЛЕНО: выбор цвета/размера текста для веса монеты
    if coin_weight == 1:
        screen.blit(coin_img, (coin_x, coin_y))
    else:
        screen.blit(gold_coin_img, (coin_x, coin_y))
        # можно добавить обводку или эффект для золотой монеты

    # счёт (правый верх)
    text = font.render(f"Coins: {score}", True, (0, 0, 0))
    screen.blit(text, (WIDTH - 150, 10))
    
    # ДОБАВЛЕНО: отображение скорости врага (для информации)
    speed_text = font.render(f"Enemy speed: {enemy_speed}", True, (0, 0, 0))
    screen.blit(speed_text, (WIDTH - 150, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()