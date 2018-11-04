import pygame
import sys


class EventLoop:
    def __init__(self, finished, settings):
        self.finished = finished
        self.settings = settings

    def __str__(self):
        return 'eventloop, filename=' + str(self.finished) + ')'

    @staticmethod
    def check_events(player):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.moving_right = True
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player.moving_down = True
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.moving_left = True
                elif event.key == pygame.K_w or event.key == pygame.K_UP: # not sure how to make him jump
                    player.moving_up = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.moving_right = False
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player.moving_down = False
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.moving_left = False
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.moving_up = False


