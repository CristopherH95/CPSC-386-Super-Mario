from animate import Animator
from coin import Coin
from item import Mushroom, FireFlower, StarMan, OneUp
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

    def check_hit(self, other):
        pass

    def blit(self):
        """Blit the block to the screen"""
        self.screen.blit(self.image, self.rect)


class BlockRubble(Sprite):
    """Sprite for pieces of a destroyed block"""
    def __init__(self, x, y, initial_image, speed_x, speed_y, screen):
        super(BlockRubble, self).__init__()
        self.image = initial_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed_x, self.speed_y = speed_x, speed_y
        self.screen = screen

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.speed_x > 0:
            self.speed_x -= 1
        else:
            self.speed_x += 1
        if self.rect.y > self.screen.get_height():
            self.kill()


class CoinBlock(Block):
    """A block which contains a number of items"""
    STD_STATE = 'std'
    HIT_STATE = 'hit'
    MOVE_UP_STATE = 'move-up'
    MOVE_DOWN_STATE = 'move-down'

    def __init__(self, x, y, initial_image, screen, map_group, rubble_group=None, coins=0, allow_hits=False):
        super(CoinBlock, self).__init__(x, y, initial_image, screen)
        self.coin_counter = int(coins)
        self.blank_img = image.load('map/super-mario-empty-block.png') if self.coin_counter > 0 else None
        self.coins = []
        self.map_group = map_group
        self.rubble_group = rubble_group
        self.allow_hits = allow_hits
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
    def coin_block_from_tmx_obj(cls, obj, screen, map_group, game_objects):
        """Create a CoinBlock object from a tmx data object"""
        return cls(obj.x, obj.y, obj.image, screen, map_group, coins=obj.properties.get('coins', 0),
                   allow_hits=obj.properties.get('allow_hits', False), rubble_group=game_objects['rubble'])

    def set_blank(self):
        """Set the block to a blank block, which cannot be hit any longer"""
        self.state['blank'] = True
        self.allow_hits = False

    def check_hit(self, other):
        """Check if the block has been hit in a way that will 'bump' its location"""
        if not self.state['blank'] or self.allow_hits:
            hit = False
            if self.rect.collidepoint(other.rect.midtop):
                hit = True
            if hit:    # leave other parameter as None to force hit state (for testing)
                other.rect.y = self.rect.bottom
                other.y_vel = 7
                print('other hit', other)
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
                elif self.rubble_group is not None and other.state_info['big']:
                    print('rubble time')
                    rubble_img = image.load('images/environment/super-mario-bricks-rubble.png')
                    speeds = [(-15, 5), (-10, 5), (10, 5), (15, 5)]
                    for speed in speeds:
                        rubble = BlockRubble(self.rect.x, self.rect.y, rubble_img, speed[0], speed[1], self.screen)
                        self.rubble_group.add(rubble)
                        self.map_group.add(rubble)
                    self.kill()

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
    MUSHROOM = 'mushroom'
    ONE_UP = '1-up'
    FIRE_FLOWER = 'fire-flower'
    STARMAN = 'starman'

    def __init__(self, x, y, screen, map_group, game_objects, item=MUSHROOM, static_img=None):
        if not static_img:
            images = ['map/Question-Block-1.png', 'map/Question-Block-2.png', 'map/Question-Block-3.png']
            self.animator = Animator(images)
            initial_image = self.animator.get_image()
        else:
            initial_image = static_img
            self.animator = None
        self.game_objects = game_objects
        if item in (QuestionBlock.MUSHROOM, QuestionBlock.FIRE_FLOWER, QuestionBlock.STARMAN, QuestionBlock.ONE_UP):
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
        item_type = obj.properties.get('item', None)
        if obj.properties.get('invisible', None):
            return cls(obj.x, obj.y, screen, map_group, game_objects, item_type, static_img=obj.image)
        return cls(obj.x, obj.y, screen, map_group, game_objects, item_type)

    def check_hit(self, other):
        points = super(QuestionBlock, self).check_hit(other)
        if self.item and self.state['meta'] == CoinBlock.HIT_STATE:
            obstacles, floor = self.game_objects['collide_objs'], self.game_objects['floors']
            if self.item == QuestionBlock.MUSHROOM and not other.state_info['big']:
                n_item = Mushroom(self.rect.x, self.rect.y, obstacles, floor, rise_from=self)
            elif self.item == QuestionBlock.ONE_UP:
                n_item = OneUp(self.rect.x, self.rect.y, obstacles, floor, rise_from=self)
            elif self.item == QuestionBlock.FIRE_FLOWER or self.item == QuestionBlock.MUSHROOM:
                n_item = FireFlower(self.rect.x, self.rect.y, obstacles, floor, rise_from=self)
            else:
                n_item = StarMan(self.rect.x, self.rect.y, obstacles, floor, rise_from=self)
            self.game_objects['items'].add(n_item)
            self.map_group.add(n_item)
            self.item = None
            self.state['blank'] = True
        elif points:
            return points

    def update(self):
        """Update the question block to its next animated image"""
        if not self.state['blank'] and self.animator:
            self.image = self.animator.get_image()
        elif self.state['blank']:
            self.image = self.blank_img
        super(QuestionBlock, self).update()
