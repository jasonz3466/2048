"""Time-based slides, tile pops, score feedback, and a few small particles."""

from dataclasses import dataclass
import math
import random
from . import settings as S
from .tile_effects import TileEffects


def ease(t):
    return 1 - (1 - max(0, min(1, t))) ** 3


def slide_ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


@dataclass
class Spark:
    x: float
    y: float
    vx: float
    vy: float
    life: float = 0.34
    age: float = 0


class Animator:
    def __init__(self, quiet=False):
        self.quiet = quiet
        self.reset()

    def reset(self, intro=True, board=None):
        self.turn, self.age, self.intro = None, 0, intro
        self.effects = TileEffects(board if intro and not self.quiet else None)
        self.sparks = []
        self.gain, self.gain_age = 0, 1
        self.landed, self.celebrated = True, False

    @property
    def busy(self):
        return not self.quiet and self.turn is not None and self.age < S.SLIDE

    @property
    def settled(self):
        return self.quiet or (not self.busy and self.effects.settled)

    @property
    def progress(self):
        return 1 if self.quiet else slide_ease(self.age / S.SLIDE)

    def start(self, turn):
        self.effects.begin(turn)
        self.turn, self.age, self.landed, self.intro = turn, 0, False, False
        if self.quiet:
            self.age = S.SLIDE + max(S.SPAWN, S.MERGE)
            self.landed = True
            self.effects = TileEffects()

    def set_quiet(self, quiet):
        self.quiet = quiet
        if quiet:
            self.age = max(self.age, S.SLIDE + max(S.SPAWN, S.MERGE))
            self.sparks.clear()
            self.effects = TileEffects()

    def scale(self, cell, travelling=False):
        return 1 if self.quiet else self.effects.scale(cell, travelling)

    def burst(self, x, y, count=6, celebration=False):
        if not self.quiet:
            for _ in range(count):
                angle, speed = random.uniform(0, math.tau), random.uniform(50, 120)
                radius = 0 if celebration else S.CELL * 0.35
                self.sparks.append(
                    Spark(
                        x + math.cos(angle) * radius,
                        y + math.sin(angle) * radius,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed - 70,
                        1.0 if celebration else 0.34,
                    )
                )

    def celebrate(self):
        self.celebrated = True
        for x in range(S.BOARD_X + 40, S.BOARD_X + S.BOARD_SIDE, 80):
            self.burst(x, S.BOARD_Y + 60, 4, celebration=True)

    def update(self, dt):
        self.age += dt
        self.effects.update(dt)
        self.gain_age += dt
        if self.turn and not self.landed and not self.busy:
            self.landed = True
            self.effects.land()
            if self.turn.points:
                self.gain, self.gain_age = self.turn.points, 0
            for cell in self.turn.merged:
                x, y = S.cell_xy(cell)
                self.burst(x + S.CELL / 2, y + S.CELL / 2)
        for spark in self.sparks:
            spark.age += dt
            spark.x += spark.vx * dt
            spark.y += spark.vy * dt + 90 * dt * dt
            spark.vy += 180 * dt
        self.sparks = [spark for spark in self.sparks if spark.age < spark.life]
