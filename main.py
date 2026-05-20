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
PIPE_GAP    = 160
RAT_X       = 90
RAT_R       = 20
PIPE_FRAMES = 90

try:
    font_lg = pygame.font.SysFont("Courier New", 42, bold=True)
    font_md = pygame.font.SysFont("Courier New", 22)
    font_sm = pygame.font.SysFont("Courier New", 15)
except Exception:
    font_lg = pygame.font.SysFont(None, 42)
    font_md = pygame.font.SysFont(None, 22)
    font_sm = pygame.font.SysFont(None, 15)

def make_stars(n=80):
    return [
        {
            "x": random.uniform(0, W),
            "y": random.uniform(0, H),
            "speed": random.uniform(0.1, 0.5),
            "bright": random.uniform(0.4, 1.0),
        }
        for _ in range(n)
    ]
def new_pipe():
    min_g = PIPE_GAP / 2 + 40
    max_g = H - PIPE_GAP / 2 - 40
    return {"x": float(W + PIPE_W), "gap_y": random.uniform(min_g, max_g), "scored": False}

def draw_bg():
    for y in range(0, H, 2):
        t = y / H
        r = int(5  + 5  * t)
        g = int(3  + 2  * t)
        b = int(15 + 22 * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (W, y))

def draw_stars(stars, tick):
    for s in stars:
        twinkle = 0.7 + 0.3 * math.sin(tick * 0.05 + s["x"])
        brightness = int(s["bright"] * twinkle * 255)
        brightness = max(0, min(255, brightness))
        color = (brightness, int(brightness * 0.9), brightness)
        radius = max(1, int(s["r"]))
        pygame.draw.circle(screen, color, (int(s["x"]), int(s["y"])), radius)

def draw_pipe(pipe):
    x      = int(pipe["x"])
    gap_y  = pipe["gap_y"]
    top_h  = int(gap_y - PIPE_GAP / 2)
    bot_y  = int(gap_y + PIPE_GAP / 2)
    bot_h  = H - bot_y

    def draw_col(px, py, pw, ph, flipped):
        if ph <= 0:
            return
        # Body — vertical gradient via columns
        for i in range(pw):
            t = (i / pw) * (1 - i / pw) * 4
            r = int(58  + 49 * t)
            g = int(42  + 34 * t)
            b = int(26  + 20 * t)
            pygame.draw.line(screen, (r, g, b), (px + i, py), (px + i, py + ph))
        # Border
        pygame.draw.rect(screen, (139, 99, 64), (px, py, pw, ph), 2)
        # Craters
        for cx_r, cy_r in [(0.3, 0.2), (0.7, 0.5), (0.5, 0.75)]:
            ccx = int(px + cx_r * pw)
            ccy_r = (1 - cy_r) if flipped else cy_r
            ccy = int(py + ccy_r * ph)
            if ccy < py or ccy > py + ph:
                continue
            cr = max(2, int(0.07 * pw))
            pygame.draw.circle(screen, (20, 12, 5), (ccx, ccy), cr)
        # Cap
        cap_h = 18
        cap_y = (py + ph - cap_h) if flipped else py
        pygame.draw.rect(screen, (192, 128, 80), (px - 6, cap_y, pw + 12, cap_h))

    draw_col(x, 0,     PIPE_W, top_h, True)
    draw_col(x, bot_y, PIPE_W, bot_h, False)

def draw_rat(surf, y, vy, tick):
    cx, cy = RAT_X, int(y)
    angle  = max(-0.45, min(0.9, vy * 0.06))

    tmp = pygame.Surface((80, 80), pygame.SRCALPHA)
    tc  = 40  # centre of temp surface

    # Body
    pygame.draw.ellipse(tmp, (138, 122, 106), (tc - 24, tc - 14, 48, 30))
    # Rear
    pygame.draw.ellipse(tmp, (122, 106, 90),  (tc - 28, tc - 10, 26, 22))
    # Head
    pygame.draw.ellipse(tmp, (192, 160, 128), (tc + 6, tc - 26, 22, 26))
    # Ear outer / inner
    pygame.draw.ellipse(tmp, (192, 160, 128), (tc - 28, tc - 28, 14, 24))
    pygame.draw.ellipse(tmp, (255, 144, 144), (tc - 26, tc - 26,  9, 16))
    # Nose
    pygame.draw.ellipse(tmp, (255,  80,  80), (tc + 22, tc - 20, 10,  8))
    pygame.draw.ellipse(tmp, (255, 140, 140), (tc + 23, tc - 19,  7,  5))
    # Whiskers
    for i, (dx, dy) in enumerate([(12, 0), (14, -4), (12, -8)]):
        pygame.draw.line(tmp, (255, 208, 176),
                         (tc + 14, tc - 18 + i * 4),
                         (tc + 14 + dx, tc - 18 + i * 4 + dy), 1)
    # Tail
    pts = [(tc - 26, tc + 14), (tc - 36, tc + 22),
           (tc - 26, tc + 34), (tc - 16, tc + 40)]
    pygame.draw.lines(tmp, (224, 192, 160), False, pts, 2)
    # Thruster glow
    flicker = 0.7 + 0.3 * math.sin(tick * 0.3)
    glow_r  = int(14 * flicker)
    for radius in range(glow_r, 0, -2):
        alpha = int(200 * (radius / glow_r))
        glow_surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (140, 100, 255, alpha),
                           (radius + 1, radius + 1), radius)
        tmp.blit(glow_surf, (tc - 30 - radius, tc + 4 - radius))
    # Helmet visor
    pygame.draw.ellipse(tmp, (192, 172, 255, 140), (tc - 4, tc - 22, 22, 14)) 

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