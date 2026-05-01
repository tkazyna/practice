import pygame
import random

W, H = 500, 600
lanes = [150, 250, 350]

CAR_COLORS = {
    "red":   (220, 50, 50),
    "blue":  (50, 80, 220),
    "green": (50, 180, 50),
}

def run(surf, clock, settings, username):
    font  = pygame.font.SysFont("Arial", 22)
    small = pygame.font.SysFont("Arial", 17)

    # difficulty settings
    speeds     = {"easy": 4, "normal": 6, "hard": 9}
    intervals  = {"easy": 110, "normal": 70, "hard": 45}
    base_spd   = speeds[settings["difficulty"]]
    spawn_rate = intervals[settings["difficulty"]]

    player_lane = 1
    px = float(lanes[1])
    py = 490
    car_col = CAR_COLORS.get(settings["color"], (220, 50, 50))

    enemies = []   # each is a dict {x, y, spd}
    coins   = []   # {x, y, val}
    obs     = []   # {x, y, kind}
    pups    = []   # {x, y, kind, life}
    strips  = []   # nitro strips {x, y}

    score  = 0
    ncoin  = 0
    dist   = 0
    frame  = 0
    road_y = 0

    shield   = False
    nitro    = False
    nitro_t  = 0
    oil_t    = 0
    active_pu = ""

    while True:
        frame += 1
        spd = base_spd + ncoin // 10  # speed increases every 10 coins
        if nitro:      spd += 4
        if oil_t > 0:  spd = max(2, spd - 3)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a)  and player_lane > 0: player_lane -= 1
                if e.key in (pygame.K_RIGHT, pygame.K_d) and player_lane < 2: player_lane += 1

        px += (lanes[player_lane] - px) * 0.2

        if nitro_t > 0:
            nitro_t -= 1
            if nitro_t == 0: nitro = False; active_pu = ""
        if oil_t > 0: oil_t -= 1

        dist  += spd
        score  = ncoin * 10 + dist // 20

        # spawn enemies
        if frame % spawn_rate == 0:
            ln = random.randint(0, 2)
            enemies.append({"x": lanes[ln], "y": -65, "spd": spd + random.randint(0, 3)})

        # spawn coins with different values (weighted)
        if frame % 40 == 0:
            ln  = random.randint(0, 2)
            val = random.choices([1, 2, 5], weights=[70, 25, 5])[0]
            coins.append({"x": lanes[ln], "y": -20, "val": val})

        # spawn obstacles: oil spill, pothole, barrier
        if frame % (spawn_rate + 30) == 0:
            ln   = random.randint(0, 2)
            kind = random.choice(["oil", "pothole", "barrier"])
            obs.append({"x": lanes[ln], "y": -25, "kind": kind})

        # spawn power-ups
        if frame % 200 == 0:
            ln = random.randint(0, 2)
            pups.append({"x": lanes[ln], "y": -25,
                         "kind": random.choice(["nitro", "shield", "repair"]),
                         "life": 290})

        # nitro strips as road events
        if frame % 185 == 0:
            ln = random.randint(0, 2)
            strips.append({"x": lanes[ln], "y": -15})

        # increase difficulty over time
        if frame % 500 == 0:
            spawn_rate = max(20, spawn_rate - 3)

        ipx = int(px)
        pr  = pygame.Rect(ipx - 18, py - 29, 36, 58)

        # enemy collisions
        for en in enemies[:]:
            en["y"] += en["spd"]
            if pygame.Rect(en["x"]-18, en["y"]-29, 36, 58).colliderect(pr):
                if shield:
                    shield = False; active_pu = ""; enemies.remove(en)
                else:
                    return score, dist // 10, ncoin
            elif en["y"] > H + 60:
                enemies.remove(en)

        # coin collisions
        for c in coins[:]:
            c["y"] += spd
            if pygame.Rect(c["x"]-10, c["y"]-10, 20, 20).colliderect(pr):
                ncoin += c["val"]; coins.remove(c)
            elif c["y"] > H + 20:
                coins.remove(c)

        # obstacle collisions
        for o in obs[:]:
            o["y"] += spd
            if pygame.Rect(o["x"]-20, o["y"]-10, 40, 20).colliderect(pr):
                if shield:
                    shield = False; active_pu = ""; obs.remove(o)
                elif o["kind"] == "oil":
                    oil_t = 120; obs.remove(o)  # slow down for 2 sec
                else:
                    return score, dist // 10, ncoin  # crash
            elif o["y"] > H + 20:
                obs.remove(o)

        # power-up collisions
        for p in pups[:]:
            p["y"] += spd; p["life"] -= 1
            if pygame.Rect(p["x"]-18, p["y"]-18, 36, 36).colliderect(pr):
                if p["kind"] == "nitro":
                    nitro = True; nitro_t = 240; active_pu = "nitro"
                elif p["kind"] == "shield":
                    shield = True; active_pu = "shield"
                elif p["kind"] == "repair":
                    obs.clear(); active_pu = "repair"  # removes all obstacles
                pups.remove(p)
            elif p["y"] > H + 20 or p["life"] <= 0:
                pups.remove(p)

        # nitro strip collisions
        for s in strips[:]:
            s["y"] += spd
            if pygame.Rect(s["x"]-18, s["y"], 36, 12).colliderect(pr):
                nitro = True; nitro_t = 180; strips.remove(s)
            elif s["y"] > H + 20:
                strips.remove(s)

        # draw road
        surf.fill((40, 40, 40))  #дорога
        pygame.draw.rect(surf, (255, 255, 255), (200, 0, 3, H))
        pygame.draw.rect(surf, (255, 255, 255), (300, 0, 3, H))

        # nitro strips
        for s in strips:
            pygame.draw.rect(surf, (230,120,0), (s["x"]-18, s["y"], 36, 12), border_radius=3)

        # obstacles
        for o in obs:
            r = pygame.Rect(o["x"]-20, o["y"]-10, 40, 20)
            if o["kind"] == "oil":
                pygame.draw.ellipse(surf, (100, 30, 150), r)
            elif o["kind"] == "pothole":
                pygame.draw.ellipse(surf, (20, 20, 20), r)
                pygame.draw.ellipse(surf, (100,100,100), r, 2)
            else:
                pygame.draw.rect(surf, (200, 40, 40), r, border_radius=3)

        # coins
        for c in coins:
            col = (230,190,0) if c["val"]==1 else (190,190,190) if c["val"]==2 else (255,140,0)
            pygame.draw.circle(surf, col, (c["x"], c["y"]), 10)
            vt = small.render(str(c["val"]), True, (0,0,0))
            surf.blit(vt, (c["x"]-vt.get_width()//2, c["y"]-vt.get_height()//2))

        # power-ups
        pu_col = {"nitro": (230,120,0), "shield": (0,200,220), "repair": (50,180,50)}
        for p in pups:
            pygame.draw.circle(surf, pu_col[p["kind"]], (p["x"], p["y"]), 18)
            pygame.draw.circle(surf, (255,255,255), (p["x"], p["y"]), 18, 2)
            lt = small.render(p["kind"][0].upper(), True, (0,0,0))
            surf.blit(lt, (p["x"]-lt.get_width()//2, p["y"]-lt.get_height()//2))

        # enemies
        for en in enemies:
            pygame.draw.rect(surf, (180,60,60), (en["x"]-18, en["y"]-29, 36, 58), border_radius=4)

        # player
        pygame.draw.rect(surf, car_col, (ipx-18, py-29, 36, 58), border_radius=4)
        if shield:
            pygame.draw.circle(surf, (0,200,220), (ipx, py), 34, 3)
        if nitro:
            pygame.draw.rect(surf, (230,120,0), (ipx-7, py+29, 14, 10), border_radius=3)

        # HUD
        pygame.draw.rect(surf, (10,10,25), (0, 0, 500, 54))
        surf.blit(font.render(f"Score: {score}",    True, (255,255,255)), (8, 7))
        surf.blit(font.render(f"Coins: {ncoin}",    True, (230,190,0)),   (8, 30))
        surf.blit(font.render(f"Dist: {dist//10}m", True, (50,200,80)),   (190, 7))
        surf.blit(small.render(username, True, (150,150,150)), (390, 8))
        if active_pu:
            surf.blit(small.render(active_pu.upper(), True, (230,120,0)), (375, 32))

        pygame.display.flip()
        clock.tick(60)