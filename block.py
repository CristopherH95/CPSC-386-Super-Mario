from animate import Animator
from coin import Coin
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


class CoinBlock(Block):
    """A block which contains a number of items"""
    STD_STATE = 'std'
    HIT_STATE = 'hit'
    MOVE_UP_STATE = 'move-up'
    MOVE_DOWN_STATE = 'move-down'

    def __init__(self, x, y, image, screen, map_group, coins=0):
        super(CoinBlock, self).__init__(x, y, image, screen)
        self.coin_counter = coins
        self.coins = []
        self.map_group = map_group
        self.state = {
            'meta': CoinBlock.STD_STATE,
            'move-state': None
        }
        self.std_location = self.rect.top
        self.hit_location = self.rect.top - int(self.rect.height * 0.5)
        # speed is a function of distance from hit location
        self.speed = -int(abs(self.rect.top - self.hit_location) * 0.25)
        self.item_location = self.rect.top - 1

    def check_hit(self, other=None):
        """Check if the block has been hit in a way that will 'bump' its location"""
        hit = False
        if other is not None:
            top_points = [other.rect.topleft, other.rect.midtop, other.rect.topright]
            for pt in top_points:
                if self.rect.collidepoint(pt):
                    hit = True
                    break
        if hit or other is None:    # leave other parameter as None to force hit state (for testing)
            if not self.state['meta'] == CoinBlock.HIT_STATE:
                self.state['meta'] = CoinBlock.HIT_STATE
                self.state['move-state'] = CoinBlock.MOVE_UP_STATE
            if self.coin_counter > 0:
                self.coin_counter -= 1  # deduct coin counter
                x_pos = self.rect.left + int(self.rect.width * 0.25)
                n_coin = Coin(x_pos, 0, self.screen)   # create new coin and move it to above the block
                n_coin.rect.bottom = self.item_location
                self.coins.append([n_coin, self.speed * 2])  # coin object, and speed
                self.map_group.add(n_coin)
                return n_coin.points

    def update_coins(self):
        """Update all coins in the air over the block"""
        remove = []
        for coin_num in range(len(self.coins)):
            self.coins[coin_num][0].update()
            self.coins[coin_num][0].rect.y += self.coins[coin_num][1]   # move with each coin's speed value
            self.coins[coin_num][1] += 1    # update the speed for 'gravity'
            if self.coins[coin_num][0].rect.y >= self.rect.top:
                self.coins[coin_num][0].kill()
                remove.append(coin_num)
        if remove:
            for num in sorted(remove, reverse=True):
                del self.coins[num]

    def update(self):
        """Update the block location and any coins"""
        if self.state['meta'] == CoinBlock.HIT_STATE:
            if self.state['move-state'] == CoinBlock.MOVE_UP_STATE:
                if self.rect.top <= self.hit_location:
                    self.state['move-state'] = CoinBlock.MOVE_DOWN_STATE
                else:
                    self.rect.top += self.speed
            else:
                if self.rect.top >= self.std_location:
                    self.rect.top = self.std_location   # ensure the position is exactly the same as original
                    self.state['move-state'] = None
                    self.state['meta'] = CoinBlock.STD_STATE
                else:
                    self.rect.top -= self.speed
        self.update_coins()


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
