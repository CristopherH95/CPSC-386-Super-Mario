import os
import pygame as pg

keybinding = {
    'action': pg.K_LSHIFT,
    'jump': pg.K_SPACE,
    'left': pg.K_LEFT,
    'right': pg.K_RIGHT,
    'down': pg.K_DOWN
}


def load_all_sfx(directory, accept=('.wav', '.mpe', '.ogg', '.mdi')):
    effects = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects
