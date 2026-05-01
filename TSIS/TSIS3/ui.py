import pygame

font = None
small = None

def init_fonts():
    global font, small
    font = pygame.font.SysFont("Arial", 26)
    small = pygame.font.SysFont("Arial", 20)

# draws a button and returns its rect
def btn(surf, text, x, y, w=200, h=44):
    r = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, (55, 55, 75), r)
    pygame.draw.rect(surf, (200, 200, 200), r, 2)
    t = font.render(text, True, (255, 255, 255))
    surf.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
    return r

def main_menu(surf, clock):
    init_fonts()
    big = pygame.font.SysFont("Arial", 52, bold=True)
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn(surf, "Play",        150, 210).collidepoint(mx, my): return "play"
                if btn(surf, "Leaderboard", 150, 265).collidepoint(mx, my): return "lb"
                if btn(surf, "Settings",    150, 320).collidepoint(mx, my): return "settings"
                if btn(surf, "Quit",        150, 375).collidepoint(mx, my): return "quit"
        surf.fill((20, 20, 40))
        t = big.render("RACER", True, (230, 190, 0))
        surf.blit(t, (250 - t.get_width()//2, 120))
        btn(surf, "Play",        150, 210)
        btn(surf, "Leaderboard", 150, 265)
        btn(surf, "Settings",    150, 320)
        btn(surf, "Quit",        150, 375)
        pygame.display.flip()
        clock.tick(60)

def ask_name(surf, clock):
    init_fonts()
    name = ""
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return ""
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name:
                    return name
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 14 and e.unicode.isprintable():
                    name += e.unicode
        surf.fill((20, 20, 40))
        surf.blit(font.render("Enter your name:", True, (255, 255, 255)), (145, 220))
        box = pygame.Rect(120, 265, 260, 40)
        pygame.draw.rect(surf, (50, 50, 70), box)
        pygame.draw.rect(surf, (255, 255, 255), box, 2)
        surf.blit(font.render(name + "|", True, (230, 190, 0)), (130, 272))
        surf.blit(small.render("Press Enter to start", True, (150, 150, 150)), (160, 320))
        pygame.display.flip()
        clock.tick(60)

def settings_screen(surf, clock, settings):
    init_fonts()
    colors = ["red", "blue", "green"]
    diffs  = ["easy", "normal", "hard"]
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return settings
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn(surf, "Back", 155, 430).collidepoint(mx, my):
                    return settings
                # click to cycle color
                if btn(surf, settings["color"], 240, 220, 130, 38).collidepoint(mx, my):
                    i = colors.index(settings["color"])
                    settings["color"] = colors[(i+1) % len(colors)]
                # click to cycle difficulty
                if btn(surf, settings["difficulty"], 240, 275, 130, 38).collidepoint(mx, my):
                    i = diffs.index(settings["difficulty"])
                    settings["difficulty"] = diffs[(i+1) % len(diffs)]
                # toggle sound
                if btn(surf, "ON" if settings["sound"] else "OFF", 240, 330, 130, 38).collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
        surf.fill((20, 20, 40))
        surf.blit(font.render("Settings", True, (255, 255, 255)), (195, 155))
        surf.blit(font.render("Car color:", True, (180, 180, 180)), (70, 227))
        surf.blit(font.render("Difficulty:", True, (180, 180, 180)), (70, 282))
        surf.blit(font.render("Sound:", True, (180, 180, 180)), (70, 337))
        btn(surf, settings["color"], 240, 220, 130, 38)
        btn(surf, settings["difficulty"], 240, 275, 130, 38)
        btn(surf, "ON" if settings["sound"] else "OFF", 240, 330, 130, 38)
        btn(surf, "Back", 155, 430)
        pygame.display.flip()
        clock.tick(60)

def leaderboard_screen(surf, clock):
    from persistence import load_scores
    init_fonts()
    data = load_scores()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn(surf, "Back", 155, 530).collidepoint(*pygame.mouse.get_pos()):
                    return
        surf.fill((20, 20, 40))
        surf.blit(font.render("Top 10", True, (230, 190, 0)), (205, 45))
        surf.blit(small.render("#   Name            Score   Dist  Coins", True, (150,150,150)), (45, 90))
        for i, d in enumerate(data):
            col = (230, 190, 0) if i == 0 else (255, 255, 255)
            row = f"{i+1:<4}{d['name']:<18}{d['score']:<8}{d['dist']:<6}{d['coins']}"
            surf.blit(small.render(row, True, col), (45, 118 + i * 34))
        btn(surf, "Back", 155, 530)
        pygame.display.flip()
        clock.tick(60)

def gameover_screen(surf, clock, score, dist, coins):
    init_fonts()
    big = pygame.font.SysFont("Arial", 48, bold=True)
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn(surf, "Retry",     150, 385).collidepoint(mx, my): return "retry"
                if btn(surf, "Main Menu", 150, 445).collidepoint(mx, my): return "menu"
        surf.fill((20, 20, 40))
        t = big.render("GAME OVER", True, (220, 50, 50))
        surf.blit(t, (250 - t.get_width()//2, 115))
        surf.blit(font.render(f"Score: {score}",    True, (255,255,255)), (170, 235))
        surf.blit(font.render(f"Distance: {dist}m", True, (255,255,255)), (150, 278))
        surf.blit(font.render(f"Coins: {coins}",    True, (255,255,255)), (170, 321))
        btn(surf, "Retry",     150, 385)
        btn(surf, "Main Menu", 150, 445)
        pygame.display.flip()
        clock.tick(60)