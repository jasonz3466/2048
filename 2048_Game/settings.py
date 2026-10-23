"""Shared constants for 2048 game."""

from pathlib import Path

SIZE = 4
TARGET = 2048
FPS = 120
INPUT_BUFFER = 2

CANVAS = (656, 872)
SLIDE, SPAWN, MERGE = 0.12, 0.18, 0.16
POP = 0.18
ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Colors
BACKGROUND = (34, 32, 26)
TEXT = (190, 173, 154)
MUTED = (159, 143, 123)
BORDER = (83, 74, 61)
PANEL = (46, 42, 33)
BOARD = (158, 139, 119)
EMPTY = (187, 172, 153)
TILE_TEXT = (119, 103, 82)
WHITE = (255, 252, 246)
ACCENT = (237, 207, 114)
BUTTON = (123, 104, 84)
BUTTON_HOVER = (145, 124, 102)
BUTTON_PRESSED = (100, 83, 65)
TILE_SHADOW = (139, 120, 100)
SUPER_TILE = (60, 58, 50)

TILES = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

BOARD_X, BOARD_Y, BOARD_SIDE = 40, 216, 576
PADDING, GAP = 12, 8
CELL = (BOARD_SIDE - PADDING * 2 - GAP * (SIZE - 1)) // SIZE
STEP = CELL + GAP
TILE_RADIUS, BOARD_RADIUS, BUTTON_RADIUS = 12, 22, 10


def cell_xy(cell):
    row, col = cell
    return BOARD_X + PADDING + col * STEP, BOARD_Y + PADDING + row * STEP
