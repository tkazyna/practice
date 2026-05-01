import pygame
import sys
from persistence import load_settings, save_settings, save_score
from ui import main_menu, ask_name, settings_screen, leaderboard_screen, gameover_screen
from racer import run

pygame.init()

screen = pygame.display.set_mode((500, 600))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()

settings = load_settings()


def draw_road():
    screen.fill((50, 50, 50))  # просто дорога (серый фон)

    # 3 простые белые полосы
    pygame.draw.rect(screen, (255, 255, 255), (150, 0, 5, 600))
    pygame.draw.rect(screen, (255, 255, 255), (250, 0, 5, 600))
    pygame.draw.rect(screen, (255, 255, 255), (350, 0, 5, 600))


while True:
    action = main_menu(screen, clock)

    if action == "quit":
        save_settings(settings)
        pygame.quit()
        sys.exit()

    elif action == "lb":
        leaderboard_screen(screen, clock)

    elif action == "settings":
        settings = settings_screen(screen, clock, settings)
        save_settings(settings)

    elif action == "play":
        name = ask_name(screen, clock)
        if not name:
            continue

        while True:
            draw_road()  # теперь просто дорога без сложного дизайна

            score, dist, coins = run(screen, clock, settings, name)

            save_score(name, score, dist, coins)

            result = gameover_screen(screen, clock, score, dist, coins)

            if result == "menu":
                break
            elif result == "quit":
                save_settings(settings)
                pygame.quit()
                sys.exit()