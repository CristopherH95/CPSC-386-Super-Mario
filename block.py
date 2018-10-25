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
