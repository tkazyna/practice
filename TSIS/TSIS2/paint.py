
import pygame
from datetime import datetime

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 Paint")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen.fill(WHITE)

color = BLACK
brush_size = 5

drawing = False
mode = "brush"

start_pos = None
last_pos = None

temp_screen = None

# TEXT TOOL
font = pygame.font.SysFont(None, 32)
text_mode = False
text_input = ""
text_pos = (0, 0)

clock = pygame.time.Clock()
running = True


def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x, y))

    if target_color == new_color:
        return

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue

        if surface.get_at((x, y)) != target_color:
            continue

        surface.set_at((x, y), new_color)

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))


while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # MOUSE DOWN 
        if event.type == pygame.MOUSEBUTTONDOWN:

            if mode == "fill":
                flood_fill(screen, event.pos[0], event.pos[1], color)

            elif mode == "text":
                text_mode = True
                text_input = ""
                text_pos = event.pos

            else:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos
                temp_screen = screen.copy()

        # MOUSE UP
        if event.type == pygame.MOUSEBUTTONUP:

            if drawing:
                drawing = False
                end_pos = event.pos

                # RECTANGLE
                if mode == "rect":
                    rect = pygame.Rect(
                        min(start_pos[0], end_pos[0]),
                        min(start_pos[1], end_pos[1]),
                        abs(start_pos[0] - end_pos[0]),
                        abs(start_pos[1] - end_pos[1])
                    )
                    pygame.draw.rect(screen, color, rect, brush_size)

                # CIRCLE
                if mode == "circle":
                    radius_circle = int(
                        ((start_pos[0] - end_pos[0]) ** 2 +
                         (start_pos[1] - end_pos[1]) ** 2) ** 0.5
                    )
                    pygame.draw.circle(screen, color, start_pos, radius_circle, brush_size)

                # LINE
                if mode == "line":
                    pygame.draw.line(screen, color, start_pos, end_pos, brush_size)

                # SQUARE
                if mode == "square":
                    side = max(
                        abs(end_pos[0] - start_pos[0]),
                        abs(end_pos[1] - start_pos[1])
                    )

                    rect = pygame.Rect(start_pos[0], start_pos[1], side, side)
                    pygame.draw.rect(screen, color, rect, brush_size)

                # RIGHT TRIANGLE
                if mode == "right_triangle":
                    pygame.draw.polygon(screen, color, [
                        start_pos,
                        (start_pos[0], end_pos[1]),
                        end_pos
                    ], brush_size)

                # EQUILATERAL TRIANGLE
                if mode == "equilateral_triangle":
                    side = abs(end_pos[0] - start_pos[0])
                    height = int((3 ** 0.5 / 2) * side)

                    points = [
                        (start_pos[0] + side // 2, start_pos[1]),
                        (start_pos[0], start_pos[1] + height),
                        (start_pos[0] + side, start_pos[1] + height)
                    ]

                    pygame.draw.polygon(screen, color, points, brush_size)

                # RHOMBUS
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

                    pygame.draw.polygon(screen, color, points, brush_size)

        if event.type == pygame.KEYDOWN:

            # COLORS
            if event.key == pygame.K_r:
                color = RED

            if event.key == pygame.K_g:
                color = GREEN

            if event.key == pygame.K_b:
                color = BLUE

            if event.key == pygame.K_k:
                color = BLACK

            # CLEAR SCREEN
            if event.key == pygame.K_c:
                screen.fill(WHITE)

            # SAVE IMAGE
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
                pygame.image.save(screen, filename)
                print("Saved:", filename)

            # BRUSH SIZES
            if event.key == pygame.K_8:
                brush_size = 2

            if event.key == pygame.K_9:
                brush_size = 5

            if event.key == pygame.K_0:
                brush_size = 10

            # TOOLS
            if event.key == pygame.K_1:
                mode = "brush"

            if event.key == pygame.K_2:
                mode = "rect"

            if event.key == pygame.K_3:
                mode = "circle"

            if event.key == pygame.K_4:
                mode = "square"

            if event.key == pygame.K_5:
                mode = "right_triangle"

            if event.key == pygame.K_6:
                mode = "equilateral_triangle"

            if event.key == pygame.K_7:
                mode = "rhombus"

            if event.key == pygame.K_l:
                mode = "line"

            if event.key == pygame.K_e:
                mode = "eraser"

            if event.key == pygame.K_f:
                mode = "fill"

            if event.key == pygame.K_t:
                mode = "text"

            # TEXT INPUT
            if text_mode:

                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_input, True, color)
                    screen.blit(text_surface, text_pos)
                    text_mode = False

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    text_input += event.unicode

    if drawing:

        mouse_pos = pygame.mouse.get_pos()

        # BRUSH
        if mode == "brush":
            pygame.draw.line(screen, color, last_pos, mouse_pos, brush_size)
            last_pos = mouse_pos

        # ERASER
        if mode == "eraser":
            pygame.draw.line(screen, WHITE, last_pos, mouse_pos, brush_size)
            last_pos = mouse_pos

        # LIVE PREVIEW
        if mode in [
            "rect",
            "circle",
            "line",
            "square",
            "right_triangle",
            "equilateral_triangle",
            "rhombus"
        ]:

            screen.blit(temp_screen, (0, 0))

            # RECT PREVIEW
            if mode == "rect":
                rect = pygame.Rect(
                    min(start_pos[0], mouse_pos[0]),
                    min(start_pos[1], mouse_pos[1]),
                    abs(start_pos[0] - mouse_pos[0]),
                    abs(start_pos[1] - mouse_pos[1])
                )
                pygame.draw.rect(screen, color, rect, brush_size)

            # CIRCLE PREVIEW
            if mode == "circle":
                radius_circle = int(
                    ((start_pos[0] - mouse_pos[0]) ** 2 +
                     (start_pos[1] - mouse_pos[1]) ** 2) ** 0.5
                )
                pygame.draw.circle(screen, color, start_pos, radius_circle, brush_size)

            # LINE PREVIEW
            if mode == "line":
                pygame.draw.line(screen, color, start_pos, mouse_pos, brush_size)

            # SQUARE PREVIEW
            if mode == "square":
                side = max(
                    abs(mouse_pos[0] - start_pos[0]),
                    abs(mouse_pos[1] - start_pos[1])
                )

                rect = pygame.Rect(start_pos[0], start_pos[1], side, side)
                pygame.draw.rect(screen, color, rect, brush_size)

            # RIGHT TRIANGLE PREVIEW
            if mode == "right_triangle":
                pygame.draw.polygon(screen, color, [
                    start_pos,
                    (start_pos[0], mouse_pos[1]),
                    mouse_pos
                ], brush_size)

            # EQUILATERAL TRIANGLE PREVIEW
            if mode == "equilateral_triangle":
                side = abs(mouse_pos[0] - start_pos[0])
                height = int((3 ** 0.5 / 2) * side)

                points = [
                    (start_pos[0] + side // 2, start_pos[1]),
                    (start_pos[0], start_pos[1] + height),
                    (start_pos[0] + side, start_pos[1] + height)
                ]

                pygame.draw.polygon(screen, color, points, brush_size)

            # RHOMBUS PREVIEW
            if mode == "rhombus":
                cx = (start_pos[0] + mouse_pos[0]) // 2
                cy = (start_pos[1] + mouse_pos[1]) // 2
                dx = abs(mouse_pos[0] - start_pos[0]) // 2
                dy = abs(mouse_pos[1] - start_pos[1]) // 2

                points = [
                    (cx, cy - dy),
                    (cx + dx, cy),
                    (cx, cy + dy),
                    (cx - dx, cy)
                ]

                pygame.draw.polygon(screen, color, points, brush_size)

    # TEXT PREVIEW
    if text_mode:
        preview_surface = font.render(text_input, True, color)
        screen.blit(preview_surface, text_pos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
