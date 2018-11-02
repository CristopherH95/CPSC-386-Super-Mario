from animate import Animator
import pygame


class Player(pygame.sprite.Sprite):
    """Represents the player, mario, that can be controlled by the user"""
    def __init__(self, x, y, obstacles, floor):
        self.animator = Animator(None)   # TODO
        self.image = self.animator.get_image()   # TODO
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.obstacles, self.floor = obstacles, floor
        self.speed_x, self.speed_y = 0, 0
        self.move_flags = {
            'right': False,
            'left': False,
            'down': False,
            'up': False
        }
        self.action_map = {pygame.KEYDOWN: self.set_move, pygame.KEYUP: self.unset_move}
        super(Player, self).__init__()

    def set_move(self, event):
        """Set move flags based on key events"""
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self.move_flags['right'] = True
        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self.move_flags['down'] = True
        elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self.move_flags['left'] = True
        elif event.key == pygame.K_w or event.key == pygame.K_UP:  # not sure how to make him jump
            self.move_flags['up'] = True

    def unset_move(self, event):
        """Unset move flags based on key events"""
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self.move_flags['right'] = False
        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self.move_flags['down'] = False
        elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self.move_flags['left'] = False
        elif event.key == pygame.K_w or event.key == pygame.K_UP:
            self.move_flags['up'] = False
