"""Button definitions, hit testing, and hover/press/focus drawing."""

import pygame
from . import settings as S


def make_buttons(game, quiet, overlay=None):
    undo = game.previous is not None
    if overlay:
        won = overlay == "won"
        return [
            (
                "continue" if won else "new",
                "Keep playing" if won else "New game",
                pygame.Rect(136, 544, 176, 48),
                True,
            ),
            (
                "new" if won else "undo",
                "New game" if won else "Undo",
                pygame.Rect(344, 544, 176, 48),
                won or undo,
            ),
        ]
    return [
        ("new", "New Game", pygame.Rect(472, 128, 144, 40), True),
        ("undo", "Undo", pygame.Rect(40, 128, 104, 40), undo),
        (
            "motion",
            "Motion: off" if quiet else "Motion: on",
            pygame.Rect(156, 128, 152, 40),
            True,
        ),
    ]


def hit_test(buttons, point):
    return next(
        (
            action
            for action, _, rect, enabled in buttons
            if enabled and point is not None and rect.collidepoint(point)
        ),
        None,
    )


def draw_buttons(graphics, surface, buttons, mouse=None, focus=None, pressed=None):
    for index, (action, words, rect, enabled) in enumerate(buttons):
        hover = enabled and mouse is not None and rect.collidepoint(mouse)
        primary = index == 0 and enabled
        fill = S.BUTTON if primary else S.BACKGROUND
        if hover:
            fill = S.BUTTON_HOVER if primary else S.PANEL
        down = hover and pressed == action
        if down:
            fill = S.BUTTON_PRESSED if primary else S.BORDER
        box = rect.move(0, 1 if down else 0)
        pygame.draw.rect(surface, fill, box, border_radius=S.BUTTON_RADIUS)
        pygame.draw.rect(
            surface, S.BUTTON if primary else S.BORDER, box, 1, S.BUTTON_RADIUS
        )
        color = S.WHITE if primary else S.TEXT if enabled else S.MUTED
        graphics.text(surface, words, box, 16, color, True, "center")
        if enabled and focus == action:
            pygame.draw.rect(surface, S.ACCENT, rect.inflate(8, 8), 2, S.BUTTON_RADIUS)
