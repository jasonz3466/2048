"""Keep tile growth and merge pulses alive while another move is sliding."""

from dataclasses import dataclass

from . import settings as S


@dataclass(frozen=True)
class Pulse:
    kind: str
    starts_at: float

    @property
    def duration(self):
        return S.SPAWN if self.kind == "spawn" else S.MERGE


def ease_out(t):
    return 1 - (1 - t) ** 3


class TileEffects:
    def __init__(self, board=None):
        self.time = 0
        self.current = {}
        self.travelling = {}
        if board is not None:
            self.current = {
                (r, c): Pulse("spawn", 0)
                for r, row in enumerate(board)
                for c, value in enumerate(row)
                if value
            }

    def begin(self, turn):
        # Surviving tiles carry their original effect to their new cell.
        self.travelling = self.current
        self.current = {
            end: self.travelling[start]
            for _, start, end in turn.paths
            if end not in turn.merged and start in self.travelling
        }
        arrival = self.time + S.SLIDE
        for cell in turn.merged:
            self.current[cell] = Pulse("merge", arrival)
        if turn.spawned is not None:
            self.current[turn.spawned] = Pulse("spawn", arrival)

    def update(self, dt):
        self.time += dt
        for effects in (self.current, self.travelling):
            for cell, pulse in list(effects.items()):
                if self.time - pulse.starts_at >= pulse.duration:
                    del effects[cell]

    def land(self):
        self.travelling.clear()

    @property
    def settled(self):
        return not self.current and not self.travelling

    def scale(self, cell, travelling=False):
        effects = self.travelling if travelling else self.current
        pulse = effects.get(cell)
        if pulse is None:
            return 1
        t = max(0, min(1, (self.time - pulse.starts_at) / pulse.duration))
        if pulse.kind == "spawn":
            u = t - 1
            return 0.15 + 0.85 * (1 + 2.7 * u**3 + 1.7 * u**2)
        if t < 0.4:
            return 1 + S.POP * ease_out(t / 0.4)
        if t < 0.75:
            return 1 + S.POP - (S.POP + 0.01) * ease_out((t - 0.4) / 0.35)
        return 0.99 + 0.01 * ease_out((t - 0.75) / 0.25)
