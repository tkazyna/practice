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

            # ===== НОВЫЕ ФИГУРЫ =====
            
            # КВАДРАТ
            if mode == "square":
                side = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
                rect = pygame.Rect(start_pos[0], start_pos[1], side, side)
                pygame.draw.rect(screen, color, rect, 2)

            # ПРЯМОУГОЛЬНЫЙ ТРЕУГОЛЬНИК
            if mode == "right_triangle":
                pygame.draw.polygon(screen, color, [
                    start_pos,
                    (start_pos[0], end_pos[1]),
                    end_pos
                ], 2)

            # РАВНОСТОРОННИЙ ТРЕУГОЛЬНИК
            if mode == "equilateral_triangle":
                side = abs(end_pos[0] - start_pos[0])
                height = int((3 ** 0.5 / 2) * side)
                points = [
                    (start_pos[0] + side // 2, start_pos[1]),
                    (start_pos[0], start_pos[1] + height),
                    (start_pos[0] + side, start_pos[1] + height)
                ]
                pygame.draw.polygon(screen, color, points, 2)

            # РОМБ
            if mode == "rhombus":
                cx = (start_pos[0] + end_pos[0]) // 2
                cy = (start_pos[1] + end_pos[1]) // 2
                dx = abs(end_pos[0] - start_pos[0]) // 2
                dy = abs(end_pos[1] - start_pos[1]) // 2
                points = [
                    (cx, cy - dy),
                    (cx + dx, cy),
                    (cx, cy + dy),
                    (cx - dx, cy)
                ]
                pygame.draw.polygon(screen, color, points, 2)

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
            
            # ===== НОВЫЕ КЛАВИШИ ДЛЯ ФИГУР =====
            if event.key == pygame.K_4:
                mode = "square"
            if event.key == pygame.K_5:
                mode = "right_triangle"
            if event.key == pygame.K_6:
                mode = "equilateral_triangle"
            if event.key == pygame.K_7:
                mode = "rhombus"

    if drawing:
        mouse_pos = pygame.mouse.get_pos()

        if mode == "brush":
            pygame.draw.circle(screen, color, mouse_pos, radius)

        if mode == "eraser":
            pygame.draw.circle(screen, (255, 255, 255), mouse_pos, radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()