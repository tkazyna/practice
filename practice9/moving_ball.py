import pygame

pygame.init()
screen = pygame.display.set_mode((490, 490))
clock = pygame.time.Clock()

x, y = 25, 25
radius = 25
step = 20


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_DOWN] and y + radius + step <= 490:

        y += step
    if pressed[pygame.K_UP] and y - radius - step >= 0:
        y -= step
    if pressed[pygame.K_RIGHT] and x + radius + step <= 490:
        x += step
    if pressed[pygame.K_LEFT] and x - radius - step >= 0:
        x -= step

    screen.fill((255, 255, 255))

    pygame.draw.circle( screen, (220, 0, 0), (x, y), radius)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()