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

