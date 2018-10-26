from animate import Animator
from pygame.sprite import Sprite


class Block(Sprite):
    """Generic sprite for a block/wall"""
    def __init__(self, x, y, image, screen):
        super(Block, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.screen = screen

    def blit(self):
        """Blit the block to the screen"""
        self.screen.blit(self.image, self.rect)


class QuestionBlock(Block):
    """Represents a question block which can be hit to release an item"""
    MUSHROOM = 0    # TODO: identifiers for item types

    def __init__(self, x, y, screen, item=MUSHROOM):
        images = ['map/Question-Block-1.png', 'map/Question-Block-2.png', 'map/Question-Block-3.png']
        self.animator = Animator(images)
        image = self.animator.get_image()
        self.item = item    # TODO: items
        super(QuestionBlock, self).__init__(x, y, image, screen)

    def update(self):
        """Update the question block to its next animated image"""
        self.image = self.animator.get_image()
