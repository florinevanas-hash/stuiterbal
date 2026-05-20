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
  




