import pygame
from pygame import mixer

NUMBER_OF_CHANNELS = 4
BACKGROUND_VOLUME = 1
ENEMY_VOLUME = 0.5
OBJECT_VOLUME = 0.7
MARIO_VOLUME = 0.5
SOUNDS = []


def initialize_music():
    pygame.mixer.init()
    mixer.set_num_channgels(NUMBER_OF_CHANNELS)
    add_sound()


def add_sound(sound, volume):
    sound_file = "music"
    mario_jump = pygame.mixer.Sound("media/sounds/mario/jump.wav")  # [0] Mario jumping
    mario_jump.set_volume(.05)
    SOUNDS.append(mario_jump)


def play(request):
    pygame.mixer.Sound.play(SOUNDS[request])
