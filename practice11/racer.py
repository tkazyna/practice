import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Advanced")

clock = pygame.time.Clock()

background = pygame.image.load('resour/road.png')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_img = pygame.image.load("resour/player.png")
player_img = pygame.transform.scale(player_img, (60, 80))

enemy_img = pygame.image.load("resour/Enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (60, 80))

coin_img = pygame.image.load("resour/coin2.png")
coin_img = pygame.transform.scale(coin_img, (40, 40))

font = pygame.font.SysFont("Arial", 24)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # границы экрана
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.speed = 5
        self.reset()

    def reset(self):
        self.rect.x = random.randint(50, WIDTH - 100)
        self.rect.y = -100

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.reset()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # только ВЕС (скорость одинаковая)
        self.weight = random.choice([1, 2, 3])

        self.rect.x = random.randint(50, WIDTH - 100)
        self.rect.y = -50

    def update(self):
        # одинаковая скорость для всех монет
        self.rect.y += 5

        if self.rect.top > HEIGHT:
            self.reset()


player = Player()
enemy = Enemy()
coin = Coin()

all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

all_sprites.add(player, enemy, coin)
enemy_group.add(enemy)
coin_group.add(coin)

score = 0
N = 5
current_weight = 1

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    # ускорение врага каждые N монет
    enemy.speed = 5 + score // N

    if pygame.sprite.spritecollideany(player, enemy_group):
        print("Game Over")
        pygame.time.delay(2000)
        running = False

    if pygame.sprite.spritecollideany(player, coin_group):
        score += coin.weight
        current_weight = coin.weight
        coin.reset()

    screen.blit(background, (0, 0))

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    # -------- HUD --------
    info = font.render(
        f"Coins: {score} | Enemy Speed: {enemy.speed} | Coin Weight: {current_weight}",
        True,
        (0, 0, 0)
    )
    screen.blit(info, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()