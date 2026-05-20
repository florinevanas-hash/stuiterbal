import pygame
import math
import random

pygame.init()

W, H = 480, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Space Rat")
clock = pygame.time.Clock()

GRAVITY     = 0.45
FLAP        = -8.5
PIPE_SPEED  = 2.8
PIPE_W      = 60
PIPE_GAP    = 200
RAT_X       = 90
RAT_R       = 20
PIPE_FRAMES = 90
TRAIL_LEN     = 18

RAINBOW = [
    (255, 0,   0),
    (255, 127, 0),
    (255, 220, 0),
    (0,   220, 0),
    (0,   100, 255),
    (80,  0,   200),
    (200, 0,   200),
]

try:
    font_xl = pygame.font.SysFont("Courier New", 46, bold=True)
    font_lg = pygame.font.SysFont("Courier New", 38, bold=True)
    font_md = pygame.font.SysFont("Courier New", 22, bold=True)
    font_sm = pygame.font.SysFont("Courier New", 15)
except Exception:
    font_xl = pygame.font.SysFont(None, 46)
    font_lg = pygame.font.SysFont(None, 38)
    font_md = pygame.font.SysFont(None, 22)
    font_sm = pygame.font.SysFont(None, 15)


def make_stars(n=200):
    return [
        {
            "x": random.uniform(0, W),
            "y": random.uniform(0, H),
            "r": random.uniform(0.5, 2.2),
            "speed": random.uniform(0.1, 0.5),
            "bright": random.uniform(0.4, 1.0),
            "phase": random.uniform(0, math.pi * 2),
        }
        for _ in range(n)
    ]

def make_planets():
    return [
        {"x": 380.0, "y": 520, "r": 90,  "speed": 0.18,
         "color": (90, 20, 130),  "band": (60, 10, 90),   "ring": False},
        {"x": 60.0,  "y": 130, "r": 50,  "speed": 0.10,
         "color": (20, 70, 110),  "band": (10, 40, 70),   "ring": False},
        {"x": 450.0, "y": 340, "r": 110, "speed": 0.08,
         "color": (110, 55, 15), "band": (80, 35, 8),     "ring": True},
    ]

def make_comets():
    return [
        {"x": -200.0, "y": random.uniform(30, H - 30),
         "speed": random.uniform(4, 7), "tail": random.randint(80, 150),
         "active": False, "timer": random.randint(60, 300)},
        {"x": -200.0, "y": random.uniform(30, H - 30),
         "speed": random.uniform(3, 6), "tail": random.randint(60, 120),
         "active": False, "timer": random.randint(200, 500)},
    ]

def new_pipe():
    min_g = PIPE_GAP / 2 + 40
    max_g = H - PIPE_GAP / 2 - 40
    return {"x": float(W + PIPE_W), "gap_y": random.uniform(min_g, max_g), "scored": False}

bg_surface = pygame.Surface((W, H))
for _y in range(H):
    t = _y / H
    r = int(6  + 14 * t)
    g = int(0  + 3  * t)
    b = int(14 + 40 * t)
    pygame.draw.line(bg_surface, (r, g, b), (0, _y), (W, _y))

def draw_planet(surf, p):
    cx, cy, r = int(p["x"]), int(p["y"]), int(p["r"])
    cr, cg, cb = p["color"]

    # Draw planet layers from outside in for a lit-sphere look
    for i in range(r, 0, -1):
        t = i / r
        dr = int(cr * t * 0.9)
        dg = int(cg * t * 0.9)
        db = int(cb * t * 0.9)
        pygame.draw.circle(surf, (dr, dg, db), (cx, cy), i)

    # Highlight (top-left)
    hi_r = r // 3
    hi_surf = pygame.Surface((hi_r * 2, hi_r * 2), pygame.SRCALPHA)
    pygame.draw.circle(hi_surf, (255, 255, 255, 35), (hi_r, hi_r), hi_r)
    surf.blit(hi_surf, (cx - r // 2 - hi_r, cy - r // 2 - hi_r))

# Bands
    br, bg2, bb = p["band"]
    band_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    band_surf.set_clip(pygame.Rect(1, 1, r * 2, r * 2))
    for i, frac in enumerate([-0.25, 0.1, 0.45]):
        band_y = int(r + frac * r)
        bh = max(2, r // 8)
        ba = pygame.Surface((r * 2, bh), pygame.SRCALPHA)
        ba.fill((br, bg2, bb, 60 + i * 15))
        band_surf.blit(ba, (0, band_y))
    surf.blit(band_surf, (cx - r - 1, cy - r - 1))
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx, cy), r, 1)

 # Ring
    if p["ring"]:
        ring_surf = pygame.Surface((r * 4, r * 2), pygame.SRCALPHA)
        for ri, (rr_fac, alpha) in enumerate([(1.45, 80), (1.6, 55), (1.78, 35)]):
            rr = int(r * rr_fac)
            pygame.draw.ellipse(ring_surf, (200, 150, 80, alpha),
                                (r * 2 - rr, r - max(3, ri + 2), rr * 2, max(5, (ri + 1) * 4)), 4)
        surf.blit(ring_surf, (cx - r * 2, cy - r))

def draw_comet(surf, c):
    if not c["active"]:
        return
    x, y, tl = int(c["x"]), int(c["y"]), int(c["tail"])
    steps = 12
    for i in range(steps):
        t = i / steps
        alpha = int((1 - t) * 200)
        tx = x + int(t * tl)
        ty = y - int(t * tl * 0.3)
        col_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(col_surf, (180 + int(t * 75), 200 + int(t * 55), 255, alpha), (2, 2), max(1, int((1 - t) * 3)))
        surf.blit(col_surf, (tx - 2, ty - 2))
    pygame.draw.circle(surf, (255, 255, 255), (x, y), 3)


# ── Drawing ────────────────────────────────────────────────────────────────────

def draw_stars(surf, stars, tick):
    for s in stars:
        twinkle = 0.6 + 0.4 * math.sin(tick * 0.04 + s["phase"])
        brightness = int(s["bright"] * twinkle * 255)
        brightness = max(0, min(255, brightness))
        color = (brightness, int(brightness * 0.9), brightness)
        r = max(1, int(s["r"]))
        if r > 1:
            pygame.draw.rect(surf, color, (int(s["x"]), int(s["y"]), r, r))
        else:
            pygame.draw.circle(surf, color, (int(s["x"]), int(s["y"])), 1)


def draw_trail(surf, trail):
    n = len(trail)
    if n < 2:
        return
    for i in range(n - 1):
        t = i / (n - 1)
        ci = int(t * (len(RAINBOW) - 1))
        r, g, b = RAINBOW[ci]
        alpha = int(t * 190)
        lw = max(1, int(t * 8))
        x1, y1 = int(trail[i][0]),   int(trail[i][1])
        x2, y2 = int(trail[i+1][0]), int(trail[i+1][1])
        line_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(line_surf, (r, g, b, alpha), (x1, y1), (x2, y2), lw)
        surf.blit(line_surf, (0, 0))


def draw_pipe(surf, pipe):
    x      = int(pipe["x"])
    gap_y  = pipe["gap_y"]
    top_h  = int(gap_y - PIPE_GAP / 2)
    bot_y  = int(gap_y + PIPE_GAP / 2)
    bot_h  = H - bot_y

    def draw_col(px, py, pw, ph, flipped):
        if ph <= 0:
            return
        # Base dark rock
        for i in range(pw):
            shade = int(30 + 20 * math.sin(i / pw * math.pi))
            pygame.draw.line(surf, (shade + 8, shade + 4, shade), (px + i, py), (px + i, py + ph))
        pygame.draw.rect(surf, (20, 12, 5, 120), (px, py, pw, ph))
        pygame.draw.rect(surf, (74, 56, 40), (px, py, pw, ph), 2)
        # Crystal gems
        gems = [(0.2, 0.25), (0.55, 0.5), (0.75, 0.15), (0.35, 0.72)]
        for gx_r, gy_r in gems:
            gx = int(px + gx_r * pw)
            gy_raw = (1 - gy_r) if flipped else gy_r
            gy = int(py + gy_raw * ph)
            if gy < py or gy > py + ph:
                continue
            gs = max(3, int(pw * 0.09))
            gem_surf = pygame.Surface((gs * 2 + 2, gs * 2 + 2), pygame.SRCALPHA)
            pts = [(gs, 0), (gs * 2, gs), (gs, gs * 2), (0, gs)]
            pygame.draw.polygon(gem_surf, (80, 120, 200, 140), pts)
            pygame.draw.polygon(gem_surf, (160, 210, 255, 180), pts, 1)
            surf.blit(gem_surf, (gx - gs, gy - gs))
        # Cap
        cap_h = 16
        cap_y = (py + ph - cap_h) if flipped else py
        pygame.draw.rect(surf, (106, 72, 40), (px - 5, cap_y, pw + 10, cap_h))
        pygame.draw.rect(surf, (138, 96, 48), (px - 5, cap_y, pw + 10, 4))

    draw_col(x, 0,     PIPE_W, top_h, True)
    draw_col(x, bot_y, PIPE_W, bot_h, False)


def draw_rat(surf, y, vy, tick):
    cx, cy = RAT_X, int(y)
    angle  = max(-0.45, min(0.7, vy * 0.055))

    tmp = pygame.Surface((90, 110), pygame.SRCALPHA)
    tc  = 44  # centre x/y in temp surface

    # Tail
    pts = [(tc, tc + RAT_R + 4),   # beginpunt
        (tc - 10, tc + RAT_R + 10),  # naar links
        (tc + 8,  tc + RAT_R + 20),  # naar rechts
        (tc - 6,  tc + RAT_R + 30),  # weer naar links
        (tc + 12, tc + RAT_R + 40)]

    pygame.draw.lines(tmp, (200, 160, 96), False, pts, 3)

    # Legs
    pygame.draw.ellipse(tmp, (200, 160, 96), (tc - 16, tc + RAT_R - 2, 12,  8))
    pygame.draw.ellipse(tmp, (200, 160, 96), (tc + 4,  tc + RAT_R - 2, 12,  8))

    # Helmet shadow
    pygame.draw.circle(tmp, (0, 0, 0, 70), (tc + 1, tc + 1), RAT_R + 1)

    # Helmet glass bubble
    pygame.draw.circle(tmp, (60, 100, 200, 30), (tc, tc), RAT_R)
    pygame.draw.circle(tmp, (180, 230, 255, 210), (tc, tc), RAT_R, 3)

    # Rat body inside helmet
    # Clip to circle (draw inside area only)
    inner_surf = pygame.Surface((RAT_R * 2, RAT_R * 2), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(inner_surf, (154, 138, 112), (RAT_R - 13, RAT_R - 5,  26, 20))
    # Head
    pygame.draw.ellipse(inner_surf, (176, 152, 120), (RAT_R - 11, RAT_R - 16, 22, 22))
    # Ears
    pygame.draw.ellipse(inner_surf, (176, 152, 120), (RAT_R - 18, RAT_R - 24, 10, 14))
    pygame.draw.ellipse(inner_surf, (232, 144, 144), (RAT_R - 17, RAT_R - 23,  6, 10))
    pygame.draw.ellipse(inner_surf, (176, 152, 120), (RAT_R + 8,  RAT_R - 24, 10, 14))
    pygame.draw.ellipse(inner_surf, (232, 144, 144), (RAT_R + 9,  RAT_R - 23,  6, 10))
    # Eyes (pixel squares)
    pygame.draw.rect(inner_surf, (10, 10, 20),    (RAT_R - 7, RAT_R - 12, 5, 5))
    pygame.draw.rect(inner_surf, (10, 10, 20),    (RAT_R + 3, RAT_R - 12, 5, 5))
    pygame.draw.rect(inner_surf, (255, 255, 255), (RAT_R - 6, RAT_R - 12, 2, 2))
    pygame.draw.rect(inner_surf, (255, 255, 255), (RAT_R + 4, RAT_R - 12, 2, 2))
    # Nose
    pygame.draw.ellipse(inner_surf, (224, 80, 96), (RAT_R - 3, RAT_R - 5, 6, 5))
    # Whiskers
    for wx, wy, wx2, wy2 in [
        (RAT_R - 3, RAT_R - 5, RAT_R - 14, RAT_R - 7),
        (RAT_R - 3, RAT_R - 4, RAT_R - 15, RAT_R - 3),
        (RAT_R + 3, RAT_R - 5, RAT_R + 14, RAT_R - 7),
        (RAT_R + 3, RAT_R - 4, RAT_R + 15, RAT_R - 3),
    ]:
        pygame.draw.line(inner_surf, (255, 230, 180, 200), (wx, wy), (wx2, wy2), 1)

    # Clip inner_surf to circle mask
    mask = pygame.Surface((RAT_R * 2, RAT_R * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (RAT_R, RAT_R), RAT_R - 2)
    inner_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    tmp.blit(inner_surf, (tc - RAT_R, tc - RAT_R))

    # Glint reflection
    glint = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.arc(glint, (255, 255, 255, 115), (0, 0, 12, 12),
                    math.pi * 0.1, math.pi * 1.2, 2)
    tmp.blit(glint, (tc - 14, tc - 12))

    rotated = pygame.transform.rotate(tmp, -math.degrees(angle))
    rw, rh  = rotated.get_size()
    surf.blit(rotated, (cx - rw // 2, cy - rh // 2))


def blit_text_centered(text, font, color, y, shadow=True):
    if shadow:
        s = font.render(text, True, (255, 255, 255, 30))
        screen.blit(s, (W // 2 - s.get_width() // 2 + 2, y + 2))
    rendered = font.render(text, True, color)
    screen.blit(rendered, (W // 2 - rendered.get_width() // 2, y))


def draw_panel(lines, px, py, pw, ph):
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((5, 3, 20, 185))
    screen.blit(panel, (px, py))
    pygame.draw.rect(screen, (80, 60, 140), (px, py, pw, ph), 2, border_radius=18)
    y_off = py + 24
    for text, font, color in lines:
        blit_text_centered(text, font, color, y_off, shadow=False)
        y_off += font.get_height() + 10


def draw_idle():
    draw_panel([
        ("SPACE RAT",              font_lg, (208, 176, 255)),
        ("Click or Space to flap", font_md, (255, 255, 255)),
        ("Navigate asteroid fields!", font_sm, (180, 160, 255)),
    ], W // 2 - 155, H // 2 - 90, 310, 170)


def draw_dead(score, best):
    draw_panel([
        ("GAME OVER",              font_lg, (255,  80,  80)),
        (f"Score: {score}",        font_md, (255, 255, 255)),
        (f"Best:  {best}",         font_md, (208, 176, 255)),
        ("Click or Space to retry",font_sm, (200, 200, 255)),
    ], W // 2 - 155, H // 2 - 110, 310, 215)


def draw_score(score):
    txt = font_lg.render(str(score), True, (255, 255, 255))
    screen.blit(txt, (W // 2 - txt.get_width() // 2, 20))


def make_state():
    return {
        "mode":        "idle",
        "rat_y":       H / 2,
        "rat_vy":      0.0,
        "pipes":       [],
        "score":       0,
        "best":        0,
        "tick":        0,
        "pipe_timer":  0,
        "dead_frames": 0,
        "stars":       make_stars(),
    }


def start_game(state):
    best = state["best"]
    state.update({
        "mode":        "playing",
        "rat_y":       H / 2,
        "rat_vy":      FLAP,
        "pipes":       [],
        "score":       0,
        "tick":        0,
        "pipe_timer":  0,
        "dead_frames": 0,
        "best":        best,
    })


def flap(state):
    if state["mode"] in ("idle", "dead"):
        start_game(state)
    elif state["mode"] == "playing":
        state["rat_vy"] = FLAP


def update(state):
    if state["mode"] != "playing":
        return

    state["tick"]       += 1
    state["pipe_timer"] += 1

    # Scroll stars
    for s in state["stars"]:
        s["x"] -= s["speed"]
        if s["x"] < 0:
            s["x"] = W
            s["y"] = random.uniform(0, H)

    # Physics
    state["rat_vy"] += GRAVITY
    state["rat_y"]  += state["rat_vy"]

    # Spawn pipes
    if state["pipe_timer"] >= PIPE_FRAMES:
        state["pipe_timer"] = 0
        state["pipes"].append(new_pipe())

    # Move pipes + score
    for p in state["pipes"]:
        p["x"] -= PIPE_SPEED
        if not p["scored"] and p["x"] + PIPE_W < RAT_X:
            p["scored"]    = True
            state["score"] += 1
            state["best"]   = max(state["best"], state["score"])

    state["pipes"] = [p for p in state["pipes"] if p["x"] + PIPE_W > -10]

    # Collision
    hitbox = RAT_R - 5
    ry     = state["rat_y"]
    dead   = ry - hitbox < 0 or ry + hitbox > H
    for p in state["pipes"]:
        if RAT_X + hitbox > p["x"] and RAT_X - hitbox < p["x"] + PIPE_W:
            if (ry - hitbox < p["gap_y"] - PIPE_GAP / 2 or
                    ry + hitbox > p["gap_y"] + PIPE_GAP / 2):
                dead = True

    if dead:
        state["mode"]        = "dead"
        state["dead_frames"] = 0

    if state["mode"] == "dead":
        state["dead_frames"] += 1


def main():
    state = make_state()
    bg_surface = pygame.Surface((W, H))
    draw_bg()  # draw the gradient once into bg_surface via screen then copy
    bg_surface.blit(screen, (0, 0))

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    flap(state)
            if event.type == pygame.MOUSEBUTTONDOWN:
                flap(state)

        update(state)

        # Render
        screen.blit(bg_surface, (0, 0))
        draw_stars(state["stars"], state["tick"])

        for p in state["pipes"]:
            draw_pipe(p)

        if state["mode"] == "idle":
            bob_y = H / 2 + math.sin(pygame.time.get_ticks() * 0.002) * 8
            draw_rat(screen, bob_y, 0, state["tick"])
            draw_idle()
        else:
            draw_rat(screen, state["rat_y"], state["rat_vy"], state["tick"])
            if state["mode"] == "playing":
                draw_score(state["score"])
            elif state["mode"] == "dead":
                draw_score(state["score"])
                if state["dead_frames"] > 20:
                    draw_dead(state["score"], state["best"])

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
