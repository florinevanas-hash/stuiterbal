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