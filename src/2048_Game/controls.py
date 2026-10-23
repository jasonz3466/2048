"""Keyboard, pointer/swipe input, held keys, and one buffered direction."""

from collections import deque

import pygame
from .screen import BOARD_RECT

KEYS = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
}
SHORTCUTS = {
    pygame.K_r: "new",
    pygame.K_u: "undo",
    pygame.K_z: "undo",
    pygame.K_m: "motion",
}


class Controls:
    def __init__(self, app):
        self.app = app
        self.clear()

    def clear(self):
        self.pending = deque()
        self.held = self.pointer = None
        self.repeat = 0.25
        self.app.view.focus = self.app.view.pressed = None

    def pointer_event(self, point, down, source):
        view = self.app.view
        if down:
            if self.pointer is None:
                action = view.button_at(point)
                self.pointer = point, source, action
                view.pressed, view.focus = action, None
            return
        if self.pointer is None or self.pointer[1] != source:
            return
        start, _, action = self.pointer
        self.pointer = view.pressed = None
        if point is None or start is None:
            return
        if action:
            if action == view.button_at(point):
                self.app.action(action)
        elif BOARD_RECT.collidepoint(start):
            dx, dy = point[0] - start[0], point[1] - start[1]
            if max(abs(dx), abs(dy)) >= 24:
                direction = (
                    ("right" if dx > 0 else "left")
                    if abs(dx) > abs(dy)
                    else ("down" if dy > 0 else "up")
                )
                self.app.request(direction)

    def handle(self, event):
        app, view = self.app, self.app.view
        if event.type == pygame.QUIT:
            app.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.clear()
        elif event.type == pygame.VIDEORESIZE:
            app.screen = pygame.display.get_surface()
            view.resize(app.screen)
            self.pointer = view.pressed = None
        elif event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            key = event.key
            if key == pygame.K_ESCAPE:
                app.running = False
            elif key in SHORTCUTS:
                app.action(SHORTCUTS[key])
            elif key in KEYS:
                self.held, self.repeat = key, 0.25
                app.request(KEYS[key])
            elif key == pygame.K_TAB:
                actions = [a for a, _, _, enabled in view.buttons() if enabled]
                step = -1 if getattr(event, "mod", 0) & pygame.KMOD_SHIFT else 1
                if view.focus in actions:
                    index = (actions.index(view.focus) + step) % len(actions)
                else:
                    index = 0 if step == 1 else -1
                view.focus = actions[index]
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                action = view.focus or ("continue" if view.overlay == "won" else "new")
                if view.focus or view.overlay:
                    app.action(action)
        elif event.type == pygame.KEYUP and event.key == self.held:
            self.held = None
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            if event.button == 1 and not getattr(event, "touch", False):
                self.pointer_event(
                    view.to_canvas(event.pos),
                    event.type == pygame.MOUSEBUTTONDOWN,
                    "mouse",
                )
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            point = event.x * app.screen.get_width(), event.y * app.screen.get_height()
            self.pointer_event(
                view.to_canvas(point), event.type == pygame.FINGERDOWN, event.finger_id
            )

    def update(self, dt):
        if self.app.game.status == "playing":
            while self.pending and not self.app.view.animator.busy:
                self.app.request(self.pending.popleft())
                if self.app.game.status != "playing":
                    break
            if self.held is not None:
                self.repeat -= dt
                if self.repeat <= 0:
                    if not self.pending:
                        self.app.request(KEYS[self.held])
                    self.repeat = 0.16
