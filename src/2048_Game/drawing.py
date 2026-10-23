"""Reusable drawing helpers. Fonts and tile faces are cached here."""

import pygame
from . import settings as S


class Graphics:
    def __init__(self, canvas):
        self.canvas = canvas
        self.fonts, self.faces = {}, {}

    def clear(self):
        self.fonts.clear()
        self.faces.clear()

    def text(
        self,
        surface,
        words,
        rect,
        size=16,
        color=S.TEXT,
        bold=False,
        align="left",
        alpha=255,
    ):
        key = size, bold
        if key not in self.fonts:
            name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
            self.fonts[key] = pygame.font.Font(str(S.ASSETS / name), size)
        image = self.fonts[key].render(str(words), True, color)
        bounds = image.get_bounding_rect()
        if not bounds.width or not bounds.height:
            return
        image = image.subsurface(bounds)
        if image.get_width() > rect.width:
            height = max(1, round(image.get_height() * rect.width / image.get_width()))
            image = pygame.transform.smoothscale(image, (rect.width, height))
        if alpha != 255:
            image = image.copy()
            image.set_alpha(alpha)
        destination = image.get_rect(center=rect.center)
        if align == "left":
            destination.left = rect.left
        elif align == "right":
            destination.right = rect.right
        surface.blit(image, destination)

    def tile(self, value, x, y, scale=1):
        if value not in self.faces:
            face = pygame.Surface((S.CELL, S.CELL), pygame.SRCALPHA)
            pygame.draw.rect(
                face,
                S.TILES.get(value, S.SUPER_TILE),
                face.get_rect(),
                border_radius=S.TILE_RADIUS,
            )
            ink = S.TILE_TEXT if value in (2, 4) else S.WHITE
            size = 52 if value < 100 else 44 if value < 1000 else 36
            self.text(
                face,
                value,
                pygame.Rect(8, 8, S.CELL - 16, S.CELL - 16),
                size,
                ink,
                True,
                "center",
            )
            self.faces[value] = face
        side = max(1, round(S.CELL * scale))
        face = self.faces[value]
        if side != S.CELL:
            face = pygame.transform.smoothscale(face, (side, side))
        rect = face.get_rect(center=(round(x + S.CELL / 2), round(y + S.CELL / 2)))
        pygame.draw.rect(
            self.canvas,
            S.TILE_SHADOW,
            rect.move(0, 2),
            border_radius=round(S.TILE_RADIUS * scale),
        )
        self.canvas.blit(face, rect)
