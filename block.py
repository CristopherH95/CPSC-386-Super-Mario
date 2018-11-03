from animate import Animator
from coin import Coin
from item import Item
from pygame import image
from pygame.sprite import Sprite


class Block(Sprite):
    """Generic sprite for a block/wall"""
    def __init__(self, x, y, initial_image, screen):
        super(Block, self).__init__()
        self.image = initial_image
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

    def __init__(self, x, y, initial_image, screen, map_group, coins=0):
        super(CoinBlock, self).__init__(x, y, initial_image, screen)
        self.coin_counter = int(coins)
        print(self.coin_counter)
        self.blank_img = image.load('map/super-mario-empty-block.png') if self.coin_counter > 0 else None
        self.coins = []
        self.map_group = map_group
        self.allow_hits = True if self.blank_img is not None else False
        self.state = {
            'meta': CoinBlock.STD_STATE,
            'move-state': None,
            'blank': not self.allow_hits
        }
        self.std_location = self.rect.top
        self.hit_location = self.rect.top - int(self.rect.height * 0.5)
        # speed is a function of distance from hit location
        self.speed = -int(abs(self.rect.top - self.hit_location) * 0.25)
        self.item_location = self.rect.top - 1

    @classmethod
    def coin_block_from_tmx_obj(cls, obj, screen, map_group):
        """Create a CoinBlock object from a tmx data object"""
        return cls(obj.x, obj.y, obj.image, screen, map_group, coins=obj.properties['coins'])

    def set_blank(self):
        """Set the block to a blank block, which cannot be hit any longer"""
        self.state['blank'] = True
        self.allow_hits = False

    def check_hit(self, other=None):
        """Check if the block has been hit in a way that will 'bump' its location"""
        if not self.state['blank'] or self.allow_hits:
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
                    if not self.coin_counter > 0:
                        self.set_blank()
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
        if self.state['blank'] and self.blank_img:
            self.image = self.blank_img
        self.update_coins()


class QuestionBlock(CoinBlock):
    """Represents a question block which can be hit to release an item"""
    MUSHROOM = 'mushroom'    # TODO: identifiers for item types
    FIRE_FLOWER = 'fire-flower'
    STARMAN = 'starman'

    def __init__(self, x, y, screen, map_group, game_objects, item=MUSHROOM):
        images = ['map/Question-Block-1.png', 'map/Question-Block-2.png', 'map/Question-Block-3.png']
        self.animator = Animator(images)
        self.game_objects = game_objects
        initial_image = self.animator.get_image()
        if item in (QuestionBlock.MUSHROOM, QuestionBlock.FIRE_FLOWER, QuestionBlock.STARMAN):
            self.item = item    # TODO: items
            coins = None
        else:
            self.item = None
            coins = 1
        super(QuestionBlock, self).__init__(x, y, initial_image, screen, map_group, coins=coins if coins else 0)
        self.blank_img = image.load('map/super-mario-empty-block.png')  # force blank image
        self.state['blank'] = False

    @classmethod
    def q_block_from_tmx_obj(cls, obj, screen, map_group, game_objects):
        """Create a question block using tmx data"""
        if 'item' in obj.properties:
            item_type = obj.properties['item']
        else:
            item_type = None
        return cls(obj.x, obj.y, screen, map_group, game_objects, item_type)

    def check_hit(self, other=None):
        if self.item:
            obstacles, floor = self.game_objects['collide_objs'], self.game_objects['floors']
            if self.item == QuestionBlock.MUSHROOM:
                initial_image = image.load('map/mushroom.png')
                n_item = Item(self.rect.x, self.rect.y, initial_image, 2, obstacles, floor, rise_from=self)
            elif self.item == QuestionBlock.FIRE_FLOWER:
                images = ['map/fire-flower-1.png', 'map/fire-flower-2.png',
                          'map/fire-flower-3.png', 'map/fire-flower-4.png']
                n_item = Item(self.rect.x, self.rect.y, images, 0,
                              obstacles, floor, rise_from=self, animated=True)
            else:
                images = ['map/starman-1.png', 'map/starman-2.png', 'map/starman-3.png', 'map/starman-4.png']
                n_item = Item(self.rect.x, self.rect.y, images, 2,
                              obstacles, floor, rise_from=self, animated=True)
            self.game_objects['items'].add(n_item)
            self.map_group.add(n_item)
            self.item = None
            self.state['blank'] = True
            super(QuestionBlock, self).check_hit(other)
        elif self.coin_counter > 0:
            super(QuestionBlock, self).check_hit(other)

    def update(self):
        """Update the question block to its next animated image"""
        if not self.state['blank']:
            self.image = self.animator.get_image()
        else:
            self.image = self.blank_img
        super(QuestionBlock, self).update()
