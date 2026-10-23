"""Run this file to start 2048 game."""

import sys
import os
from importlib import import_module

# Add the current directory (src) to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    App = import_module("2048_Game.app").App
    App(window_size=(720, 957)).run()
