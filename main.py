"""Run this file to start 2048 game."""

from importlib import import_module

if __name__ == "__main__":
    App = import_module("2048_Game.app").App
    App(window_size=(720, 957)).run()
