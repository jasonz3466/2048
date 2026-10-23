"""2048 rules. This file works without Pygame or a window."""

from dataclasses import dataclass
import random

from .settings import SIZE, TARGET


@dataclass
class Move:
    board: tuple
    paths: list
    merged: set
    points: int = 0
    spawned: tuple | None = None


def line_cells(direction, line):
    """Read a row or column starting at the edge we are moving towards"""

    if direction == "left":
        return [(line, col) for col in range(SIZE)]
    if direction == "right":
        return [(line, col) for col in reversed(range(SIZE))]
    if direction == "up":
        return [(row, line) for row in range(SIZE)]
    if direction == "down":
        return [(row, line) for row in reversed(range(SIZE))]

    raise ValueError(f"Invalid direction: {direction}")


def slide(board, direction):
    """Calculate a slide without randomness or edits to the input board"""

    output = [[0] * SIZE for _ in range(SIZE)]
    paths, merged, points = [], set(), 0

    for line in range(SIZE):
        cells = line_cells(direction, line)
        occupied = [
            (cell, board[cell[0]][cell[1]]) for cell in cells if board[cell[0]][cell[1]]
        ]
        source, target = 0, 0
        while source < len(occupied):
            origin, value = occupied[source]
            destination = cells[target]
            paths.append((value, origin, destination))
            if source + 1 < len(occupied) and occupied[source + 1][1] == value:
                paths.append((value, occupied[source + 1][0], destination))
                value *= 2
                points += value
                merged.add(destination)
                source += 2  # Consume a pair; never re-merge its result.
            else:
                source += 1
            row, col = destination
            output[row][col] = value
            target += 1
    return Move(tuple(tuple(row) for row in output), paths, merged, points)


def can_move(board):
    """Check if a move is possible in any direction."""

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]

            if not value:
                return True
            if col + 1 < SIZE and value == board[row][col + 1]:
                return True
            if row + 1 < SIZE and value == board[row + 1][col]:
                return True

    # Otherwise, all cells have been checked without finding a possible move.
    return False


class Game:
    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.new()

    def new(self):
        """Start a new game"""
        self.board = tuple((0,) * SIZE for _ in range(SIZE))
        self.score, self.moves = 0, 0
        self.continued, self.previous = False, None
        self.spawn()
        self.spawn()

    @property
    def highest(self):
        return max(max(row) for row in self.board)

    @property
    def status(self):
        if self.highest >= TARGET and not self.continued:
            return "won"

        return "playing" if can_move(self.board) else "lost"

    def spawn(self):
        empty = [
            (r, c) for r in range(SIZE) for c in range(SIZE) if not self.board[r][c]
        ]
        row, col = self.rng.choice(empty)
        rows = [list(row) for row in self.board]
        rows[row][col] = 2 if self.rng.random() < 0.9 else 4
        self.board = tuple(tuple(row) for row in rows)
        return row, col

    def move(self, direction):
        if self.status != "playing":
            return None
        result = slide(self.board, direction)
        if result.board == self.board:
            return None
        self.previous = (
            self.board,
            self.score,
            self.moves,
            self.continued,
            self.rng.getstate(),
        )
        self.board = result.board
        self.score += result.points
        self.moves += 1
        result.spawned = self.spawn()
        result.board = self.board
        return result

    def undo(self):
        if self.previous is None:
            return False
        self.board, self.score, self.moves, self.continued, state = self.previous
        self.rng.setstate(state)
        self.previous = None
        return True
