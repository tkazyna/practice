import pygame
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Advanced")

screen.fill("white")

# текущий цвет
color = (0, 0, 0)

# толщина кисти
radius = 5

# режим рисования
mode = "brush"

drawing = False
start_pos = None

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # нажали мышь
        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = pygame.mouse.get_pos()

        # отпустили мышь
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = pygame.mouse.get_pos()

            #  RECTANGLE
            if mode == "rectangle":
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(start_pos[0] - end_pos[0])
                h = abs(start_pos[1] - end_pos[1])
                pygame.draw.rect(screen, color, (x, y, w, h), 2)

            #  CIRCLE
            elif mode == "circle":
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                radius_circle = int((dx**2 + dy**2) ** 0.5)
                pygame.draw.circle(screen, color, start_pos, radius_circle, 2)

        # клавиши
        if event.type == pygame.KEYDOWN:

            #  цвета
            if event.key == pygame.K_r:
                color = (255, 0, 0)
            if event.key == pygame.K_g:
                color = (0, 255, 0)
            if event.key == pygame.K_b:
                color = (0, 0, 255)
            if event.key == pygame.K_k:
                color = (0, 0, 0)

            #  ERASER
            if event.key == pygame.K_e:
                color = (255, 255, 255)

            #  очистка
            if event.key == pygame.K_c:
                screen.fill("white")

            #  толщина
            if event.key == pygame.K_UP:
                radius = min(radius + 2, 50)
            if event.key == pygame.K_DOWN:
                radius = max(radius - 2, 1)

            #  режимы
            if event.key == pygame.K_1:
                mode = "brush"
            if event.key == pygame.K_2:
                mode = "rectangle"
            if event.key == pygame.K_3:
                mode = "circle"

    #  кисть
    if drawing and mode == "brush":
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, color, mouse_pos, radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()