"""Compose the header, board, end screens, and resizable window."""

import pygame
from . import settings as S
from .animation import Animator, ease
from .buttons import make_buttons, hit_test, draw_buttons
from .drawing import Graphics

BOARD_RECT = pygame.Rect(S.BOARD_X, S.BOARD_Y, S.BOARD_SIDE, S.BOARD_SIDE)


class Screen:
    def __init__(self, window, game, quiet=False):
        self.window, self.game = window, game
        self.canvas = pygame.Surface(S.CANVAS).convert()
        self.graphics, self.animator = Graphics(self.canvas), Animator(quiet)
        self.save_error = False
        self.resize(window)
        self.reset()

    def reset(self, intro=True):
        self.animator.reset(intro, self.game.board)
        self.focus = self.pressed = self.last_overlay = None

    @property
    def overlay(self):
        return (
            self.game.status
            if self.animator.settled and self.game.status != "playing"
            else None
        )

    def buttons(self, header=False):
        return make_buttons(
            self.game, self.animator.quiet, None if header else self.overlay
        )

    def button_at(self, point):
        return hit_test(self.buttons(), point)

    def update(self, dt):
        self.animator.update(dt)
        if self.overlay != self.last_overlay:
            self.focus = self.pressed = None
            self.last_overlay = self.overlay
        if self.overlay == "won" and not self.animator.celebrated:
            self.animator.celebrate()

    def resize(self, window):
        self.window = window
        ratio = min(window.get_width() / S.CANVAS[0], window.get_height() / S.CANVAS[1])
        self.viewport = pygame.Rect(
            0, 0, max(1, round(S.CANVAS[0] * ratio)), max(1, round(S.CANVAS[1] * ratio))
        )
        self.viewport.center = window.get_rect().center

    def to_canvas(self, point):
        if not self.viewport.collidepoint(point):
            return None
        return (
            (point[0] - self.viewport.x) * S.CANVAS[0] / self.viewport.width,
            (point[1] - self.viewport.y) * S.CANVAS[1] / self.viewport.height,
        )

    def paint_buttons(self, surface, buttons, mouse=None):
        draw_buttons(self.graphics, surface, buttons, mouse, self.focus, self.pressed)

    def draw_header(self, best, mouse):
        g, canvas = self.graphics, self.canvas
        g.text(canvas, "2048", pygame.Rect(40, 32, 248, 72), 64, bold=True)
        for rect, name, value in [
            (pygame.Rect(344, 32, 112, 72), "SCORE", self.game.score),
            (pygame.Rect(468, 32, 148, 72), "BEST", best),
        ]:
            if name == "SCORE":
                pygame.draw.rect(canvas, S.PANEL, rect, border_radius=S.BUTTON_RADIUS)
            else:
                pygame.draw.rect(canvas, S.BORDER, rect, 2, S.BUTTON_RADIUS)
            g.text(
                canvas,
                name,
                pygame.Rect(rect.x, 42, rect.width, 16),
                12,
                S.MUTED,
                True,
                "center",
            )
            g.text(
                canvas,
                value,
                pygame.Rect(rect.x + 8, 66, rect.width - 16, 28),
                28,
                bold=True,
                align="center",
            )
        buttons = self.buttons(header=True)
        if self.overlay:
            buttons = [(a, label, rect, False) for a, label, rect, _ in buttons]
        self.paint_buttons(canvas, buttons, mouse if not self.overlay else None)
        g.text(
            canvas,
            "Merge numbers. Reach 2048.",
            pygame.Rect(40, 184, 320, 16),
            12,
            S.MUTED,
        )
        g.text(
            canvas,
            f"{self.game.moves} moves",
            pygame.Rect(480, 184, 136, 16),
            12,
            S.MUTED,
            align="right",
        )

    def draw_board(self):
        g, animation = self.graphics, self.animator
        pygame.draw.rect(self.canvas, S.BOARD, BOARD_RECT, border_radius=S.BOARD_RADIUS)
        for row in range(S.SIZE):
            for col in range(S.SIZE):
                pygame.draw.rect(
                    self.canvas,
                    S.EMPTY,
                    (*S.cell_xy((row, col)), S.CELL, S.CELL),
                    border_radius=S.TILE_RADIUS,
                )
        if animation.busy:
            for value, start, end in sorted(
                animation.turn.paths, key=lambda path: path[1] != path[2]
            ):
                x, y = S.cell_xy(start)
                ex, ey = S.cell_xy(end)
                g.tile(
                    value,
                    x + (ex - x) * animation.progress,
                    y + (ey - y) * animation.progress,
                    animation.scale(start, travelling=True),
                )
        else:
            cells = [
                (r, c)
                for r in range(S.SIZE)
                for c in range(S.SIZE)
                if self.game.board[r][c]
            ]
            for cell in sorted(cells, key=animation.scale):
                g.tile(
                    self.game.board[cell[0]][cell[1]],
                    *S.cell_xy(cell),
                    animation.scale(cell),
                )

    def draw_overlay(self, mouse):
        g, animation = self.graphics, self.animator
        layer = pygame.Surface(S.CANVAS, pygame.SRCALPHA)
        pygame.draw.rect(
            layer, (*S.BACKGROUND, 205), BOARD_RECT, border_radius=S.BOARD_RADIUS
        )
        panel = pygame.Rect(112, 352, 432, 288)
        pygame.draw.rect(layer, S.PANEL, panel, border_radius=18)
        pygame.draw.rect(layer, S.BOARD, panel, 1, 18)
        won = self.overlay == "won"
        g.text(
            layer,
            "2048!" if won else "Game over",
            pygame.Rect(136, 384, 384, 48),
            32,
            bold=True,
            align="center",
        )
        for x, name, value in [
            (136, "SCORE", self.game.score),
            (344, "TOP TILE", self.game.highest),
        ]:
            g.text(
                layer, name, pygame.Rect(x, 456, 176, 16), 12, S.MUTED, align="center"
            )
            g.text(
                layer,
                f"{value:,}",
                pygame.Rect(x, 480, 176, 40),
                28,
                bold=True,
                align="center",
            )
        self.paint_buttons(layer, self.buttons(), mouse)
        g.text(
            layer,
            "Enter to continue" if won else "Enter to retry  /  U to undo",
            pygame.Rect(136, 608, 384, 16),
            12,
            S.MUTED,
            align="center",
        )
        if not animation.quiet:
            start = S.SLIDE + max(S.SPAWN, S.MERGE) if animation.turn else 0
            layer.set_alpha(round(255 * ease((animation.age - start) / 0.18)))
        self.canvas.blit(layer, (0, 0))

    def draw(self, best, mouse=None):
        g, animation, canvas = self.graphics, self.animator, self.canvas
        canvas.fill(S.BACKGROUND)
        self.draw_header(best, mouse)
        self.draw_board()
        if animation.gain and animation.gain_age < 0.55 and not animation.quiet:
            g.text(
                canvas,
                f"+{animation.gain}",
                pygame.Rect(344, round(108 - 12 * animation.gain_age), 112, 16),
                12,
                S.ACCENT,
                True,
                "center",
                round(255 * (1 - animation.gain_age / 0.55)),
            )
        if self.overlay:
            self.draw_overlay(mouse)
        if animation.sparks:
            layer = pygame.Surface(S.CANVAS, pygame.SRCALPHA)
            for spark in animation.sparks:
                color = (*S.ACCENT, round(220 * (1 - spark.age / spark.life)))
                pygame.draw.rect(layer, color, (round(spark.x), round(spark.y), 3, 3))
            canvas.blit(layer, (0, 0))
        g.text(
            canvas, "Arrows / WASD / swipe", pygame.Rect(40, 824, 272, 16), 12, S.MUTED
        )
        g.text(
            canvas,
            "R new   U undo   M motion   Esc quit",
            pygame.Rect(312, 824, 304, 16),
            12,
            S.MUTED,
            align="right",
        )
        if self.save_error:
            pygame.draw.rect(canvas, S.BACKGROUND, (40, 824, 576, 16))
            g.text(
                canvas,
                "Best score could not be saved.",
                pygame.Rect(40, 824, 576, 16),
                12,
                S.MUTED,
            )
        self.window.fill(S.BACKGROUND)
        frame = (
            canvas
            if self.viewport.size == canvas.get_size()
            else (pygame.transform.smoothscale(canvas, self.viewport.size))
        )
        self.window.blit(frame, self.viewport)
        pygame.display.flip()
        return canvas
