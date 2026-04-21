import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Paint")

screen.fill((255, 255, 255))

color = (0, 0, 0)   
radius = 10       
drawing = False    

mode = "brush"    

start_pos = None

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos  

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            if mode == "rect":
                rect = pygame.Rect(
                    min(start_pos[0], end_pos[0]),
                    min(start_pos[1], end_pos[1]),
                    abs(start_pos[0] - end_pos[0]),
                    abs(start_pos[1] - end_pos[1])
                )
                pygame.draw.rect(screen, color, rect, 2)

            if mode == "circle":
                radius_circle = int(((start_pos[0] - end_pos[0])**2 + (start_pos[1] - end_pos[1])**2) ** 0.5)
                pygame.draw.circle(screen, color, start_pos, radius_circle, 2)

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                color = (255, 0, 0)
            if event.key == pygame.K_g:
                color = (0, 255, 0)
            if event.key == pygame.K_b:
                color = (0, 0, 255)
            if event.key == pygame.K_k:
                color = (0, 0, 0)

            if event.key == pygame.K_e:
                mode = "eraser"

            if event.key == pygame.K_c:
                screen.fill((255, 255, 255))

            if event.key == pygame.K_UP:
                radius = min(radius + 2, 50)
            if event.key == pygame.K_DOWN:
                radius = max(radius - 2, 1)

            if event.key == pygame.K_1:
                mode = "brush"
            if event.key == pygame.K_2:
                mode = "rect"
            if event.key == pygame.K_3:
                mode = "circle"

    if drawing:
        mouse_pos = pygame.mouse.get_pos()

        if mode == "brush":
            pygame.draw.circle(screen, color, mouse_pos, radius)

        if mode == "eraser":
            pygame.draw.circle(screen, (255, 255, 255), mouse_pos, radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()