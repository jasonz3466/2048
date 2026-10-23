"""Connect the game, input, rendering, and saving; run one main loop."""

import pygame
from . import settings as S
from . import storage
from .game import Game
from .screen import Screen
from .controls import Controls
from .audio import load_sound


class App:
    def __init__(self, path=None, window_size=None):
        pygame.display.init()
        pygame.font.init()
        width, height = pygame.display.get_desktop_sizes()[0]
        ratio = min(
            1, max(1, width - 80) / S.CANVAS[0], max(1, height - 100) / S.CANVAS[1]
        )
        size = window_size or tuple(max(1, round(n * ratio)) for n in S.CANVAS)
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("2048")
        self.clock, self.game = pygame.time.Clock(), Game()
        self.path = path if path is not None else storage.data_path()
        self.preferences = storage.load(self.path)
        self.view = Screen(self.screen, self.game, self.preferences["reduced_motion"])
        self.controls = Controls(self)
        self.running, self.dirty, self.save_age = True, False, 0

    def request(self, direction):
        if self.game.status != "playing":
            return
        if self.view.animator.busy:
            if len(self.controls.pending) < S.INPUT_BUFFER:
                self.controls.pending.append(direction)
            return
        turn = self.game.move(direction)
        if turn:
            self.view.animator.start(turn)
            self.view.focus = None
            if self.game.score > self.preferences["best"]:
                self.preferences["best"] = self.game.score
                self.dirty, self.save_age = True, 0
            if self.game.status != "playing":
                self.controls.pending.clear()
                self.controls.held = None

    def action(self, action):
        focus = self.view.focus
        if action == "new":
            self.game.new()
            self.view.reset()
        elif action == "undo":
            if not self.game.undo():
                return
            self.view.reset(intro=False)
        elif action == "continue" and self.game.status == "won":
            self.game.continued = True
            self.view.reset(intro=False)
        elif action == "motion":
            quiet = not self.preferences["reduced_motion"]
            self.preferences["reduced_motion"] = quiet
            self.view.animator.set_quiet(quiet)
            self.dirty, self.save_age = True, 0
        self.controls.clear()
        if action == "motion":
            self.view.focus = focus

    def update(self, dt):
        self.view.update(dt)
        self.controls.update(dt)
        self.save_age += dt
        if self.dirty and self.save_age >= 0.75 and not self.view.animator.busy:
            self.persist()

    def persist(self):
        self.view.save_error = not storage.save(self.path, self.preferences)
        self.dirty = False

    def close(self):
        if self.dirty:
            self.persist()
        self.view.graphics.clear()
        pygame.quit()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(S.FPS) / 1000, 0.05)
                for event in pygame.event.get():
                    self.controls.handle(event)
                if self.running:
                    self.update(dt)
                    mouse = self.view.to_canvas(pygame.mouse.get_pos())
                    self.view.draw(self.preferences["best"], mouse)
        finally:
            self.close()
