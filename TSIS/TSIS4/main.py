
import pygame
import sys
from config import *
from db import init_db, get_or_create_player, save_result, get_leaderboard, get_best
from game import Game, load_settings, save_settings

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("eat.wav")
pygame.mixer.music.play(-1)  # -1 = зациклить

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)


def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, GRAY, rect)
    img = font.render(text, True, WHITE)
    screen.blit(img, (x + 10, y + 10))
    return rect


def menu_screen():
    username = ""

    while True:
        screen.fill(BLACK)

        draw_text("SNAKE GAME", 250, 50, GREEN)
        draw_text("Name:", 150, 140)

        input_box = pygame.Rect(150, 170, 300, 30)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        screen.blit(font.render(username, True, WHITE), (155, 175))

        play_btn = draw_button("PLAY", 150, 230, 200, 40)
        lb_btn = draw_button("LEADERBOARD", 150, 280, 200, 40)
        set_btn = draw_button("SETTINGS", 150, 330, 200, 40)
        quit_btn = draw_button("QUIT", 150, 380, 200, 40)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif e.key == pygame.K_RETURN:
                    if username != "":
                        pid = get_or_create_player(username)
                        return username, pid
                else:
                    username += e.unicode

            if e.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(e.pos):
                    if username != "":
                        pid = get_or_create_player(username)
                        return username, pid

                if lb_btn.collidepoint(e.pos):
                    leaderboard_screen()

                if set_btn.collidepoint(e.pos):
                    settings_screen()

                if quit_btn.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()


def leaderboard_screen():
    data = get_leaderboard()

    while True:
        screen.fill(BLACK)

        draw_text("LEADERBOARD", 220, 30, YELLOW)

        y = 80
        for i, (name, score, lvl, date) in enumerate(data):
            draw_text(str(i + 1) + ". " + name + " " + str(score), 150, y)
            y += 30

        back = draw_button("BACK", 250, 500, 120, 40)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(e.pos):
                    return


def settings_screen():
    settings = load_settings()

    while True:
        screen.fill(BLACK)

        draw_text("SETTINGS", 240, 50)

        sound_btn = draw_button("SOUND ON/OFF", 150, 150, 250, 40)
        color_btn = draw_button("CHANGE COLOR", 150, 220, 250, 40)
        save_btn = draw_button("SAVE & BACK", 150, 320, 250, 40)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(e.pos):
                     settings["sound"] = not settings["sound"]
                if settings["sound"]:
                     pygame.mixer.music.unpause()
                else:
                     pygame.mixer.music.pause()

                if color_btn.collidepoint(e.pos):
                    settings["snake_color"] = [255, 255, 255]  # максимально просто

                if save_btn.collidepoint(e.pos):
                    save_settings(settings)
                    return


def gameover_screen(score, level, best):
    while True:
        screen.fill(BLACK)

        draw_text("GAME OVER", 230, 120, RED)
        draw_text("Score: " + str(score), 240, 200)
        draw_text("Level: " + str(level), 240, 240)
        draw_text("Best: " + str(best), 240, 280, YELLOW)

        retry = draw_button("RETRY", 150, 360, 150, 40)
        menu = draw_button("MENU", 330, 360, 150, 40)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if retry.collidepoint(e.pos):
                    return "retry"
                if menu.collidepoint(e.pos):
                    return "menu"


def main():
    init_db()
    name, pid = menu_screen()
    best = get_best(pid)

    while True:
        game = Game(screen, pid, best)

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                game.handle_input(e)

            game.update()
            game.draw()

            pygame.display.flip()
            clock.tick(60)

            if game.over:
                break

        save_result(pid, game.score, game.level)

        if game.score > best:
            best = game.score

        res = gameover_screen(game.score, game.level, best)

        if res == "menu":
            name, pid = menu_screen()
            best = get_best(pid)


if __name__ == "__main__":
    main()