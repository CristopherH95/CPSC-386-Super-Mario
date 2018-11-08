from animate import Animator
from pygame.sprite import Sprite


class Coin(Sprite):
    """Represents a coin with an associated point value"""
    def __init__(self, x, y, screen, points=100):
        super(Coin, self).__init__()
        images = ['map/Coin-1.png', 'map/Coin-2.png', 'map/Coin-3.png', 'map/Coin-4.png']
        self.animator = Animator(images)
        self.image = self.animator.get_image()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.screen = screen
        self.points = points

    def update(self):
        """Update the coin image"""
        self.image = self.animator.get_image()

    def blit(self):
        """Blit the coin to the screen"""
        self.screen.blit(self.image, self.rect)
