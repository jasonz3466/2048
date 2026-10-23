"""Load sound files, store them, play them, and control volume/muting."""

import pygame
from . import settings as S


def load_sound(name, volume=S.DEFAULT_VOLUME):
    """Load a sound file and return a pygame Sound object"""
    path = S.SOUNDS / f"{name}.ogg"
    sound = pygame.mixer.Sound(str(path))
    sound.set_volume(volume)
    return sound
