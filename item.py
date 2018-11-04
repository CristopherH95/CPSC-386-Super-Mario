from animate import Animator
from pygame.sprite import Sprite, Group
from pygame import image as pygimg
from pygame import time
# TODO: Additional item types


class Item(Sprite):
    """Represents a generic item object in the mario game"""
    MUSHROOM = 'mushroom'
    ONE_UP = '1-up'
    FIRE_FLOWER = 'fire-flower'
    STARMAN = 'starman'

    def __init__(self, x, y, image, speed, obstacles, floor, item_type, rise_from=None, animated=False):
        super(Item, self).__init__()
        if animated:
            self.animator = Animator(image)
            self.image = self.animator.get_image()
        else:
            self.animator = None
            self.image = image
        self.item_type = item_type
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.speed = speed
        self.jump_speed = 0
        self.obstacles = obstacles  # objects that the item may collide with
        self.floor = floor      # rects for the floor
        self.rise_from = rise_from

    def rise(self):
        """Have the item rise up from another object"""
        if not self.rise_from:
            raise ValueError('Cannot rise from an object when that object is None')
        if self.rect.bottom <= self.rise_from.rect.top:
            self.rise_from = None
        else:
            self.rect.bottom -= 2

    def jump(self):
        """Have the item jump into the air"""
        if self.speed >= 0:
            self.jump_speed = -(self.speed * 5)
        else:
            self.jump_speed = (self.speed * 5)

    def flip_direction(self):
        """Flip the direction the item is moving on the x-axis"""
        self.speed = -self.speed
        self.rect.left += self.speed

    def bounce_off_obstacles(self):
        """Check if the item has hit any obstacles which cause it to bounce the other direction"""
        for obs in self.obstacles:
            pts = [obs.rect.bottomleft, obs.rect.midleft,
                   obs.rect.bottomright, obs.rect.midright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.flip_direction()
                    return
        for rect in self.floor:
            pts = [rect.midleft, rect.midright, rect.bottomleft, rect.bottomright]
            y_cap = rect.top
            for pt in pts:
                if self.rect.collidepoint(pt) or \
                        ((self.rect.left == rect.right or self.rect.right == rect.left) and self.rect.top > y_cap):
                    self.flip_direction()
                    return

    def fall(self):
        """If the item is not supported by any floor rects, then fall down"""
        falling = True
        for rect in self.floor:
            # check if bottom is at the top of the floor rect and that the x pos is within floor area
            if self.rect.bottom == rect.top and (rect.left < self.rect.center[0] < rect.right):
                self.rect.bottom = rect.top
                falling = False
                break
        if falling:
            for obj in self.obstacles:
                pts = [obj.rect.topleft, obj.rect.midtop, obj.rect.topright]
                for pt in pts:
                    if self.rect.collidepoint(pt):
                        falling = False
                        break
                if not falling:
                    break
        if falling:
            self.rect.bottom += abs(self.speed)

    def update(self):
        """Update the item position based on its speed variables"""
        if self.animator:
            self.image = self.animator.get_image()
        if not self.rise_from:
            if abs(self.jump_speed) > 0:
                self.rect.top += self.jump_speed
                self.jump_speed += 1    # simulate gravity reducing speed
            self.rect.left += self.speed
            self.bounce_off_obstacles()
            self.fall()
        else:
            self.rise()


class Mushroom(Item):
    """A mushroom power-up which can be picked up by Mario, causing size increase"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        image = pygimg.load('map/mushroom.png')
        speed = 2
        super(Mushroom, self).__init__(x, y, image, speed, obstacles, floor,
                                       Item.MUSHROOM, rise_from, animated=False)


class OneUp(Item):
    """A special mushroom which is meant to add an extra life on pickup"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        image = pygimg.load('map/mushroom-1-up.png')
        speed = 2
        super(OneUp, self).__init__(x, y, image, speed, obstacles, floor,
                                    Item.ONE_UP, rise_from, animated=False)


class FireFlower(Item):
    """A fire flower item which can be picked up by Mario, giving the ability to throw fire balls"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('map/fire-flower-1.png'), pygimg.load('map/fire-flower-2.png'),
                  pygimg.load('map/fire-flower-3.png'), pygimg.load('map/fire-flower-4.png')]
        speed = 0
        super(FireFlower, self).__init__(x, y, images, speed, obstacles,
                                         floor, Item.FIRE_FLOWER, rise_from, True)


class StarMan(Item):
    """A 'star-man' item which can be picked up by Mario, causing invincibility"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('map/starman-1.png'), pygimg.load('map/starman-2.png'),
                  pygimg.load('map/starman-3.png'), pygimg.load('map/starman-4.png')]
        speed = 2
        self.last_jump = time.get_ticks()
        self.jump_interval = 1000   # jump around every second
        super(StarMan, self).__init__(x, y, images, speed, obstacles, floor, Item.STARMAN, rise_from, True)

    def update(self):
        touch_floor = False
        for rect in self.floor:
            if self.rect.bottom >= rect.top:
                self.rect.bottom = rect.top
                touch_floor = True
                break
        if abs(self.last_jump - time.get_ticks()) > self.jump_interval and touch_floor:
            self.jump()
            self.last_jump = time.get_ticks()
        super(StarMan, self).update()


class FireBall(Sprite):
    """A fireball which can be thrown from Mario when he is in his fire flower state"""
    def __init__(self, x, y, norm_images, explode_images, obstacles, floor, speed=5):
        self.norm_animator = Animator(norm_images)
        self.explode_animator = Animator(explode_images, repeat=False)
        self.image = self.norm_animator.get_image()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.obstacles = obstacles
        self.floor = floor
        self.speed_x = speed
        self.speed_y = speed
        self.active = True
        super(FireBall, self).__init__()

    def check_hit_wall(self):
        """Check if the fireball has hit any walls"""
        for obs in self.obstacles:
            pts = [obs.rect.midleft, obs.rect.midright, obs.rect.bottomleft, obs.rect.bottomright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.active = False
                    return
        for flr_rect in self.floor:
            pts = [flr_rect.rect.midleft, flr_rect.rect.midright, flr_rect.rect.bottomleft, flr_rect.rect.bottomright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.active = False
                    return

    def apply_gravity(self):
        """Apply gravity to the fireball, bounce off of horizontal side of surfaces"""
        bounce = False
        for obs in self.obstacles:
            pts = [obs.rect.topleft, obs.rect.midtop, obs.rect.topright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    bounce = True
                    break
            if bounce:
                break
        if not bounce:
            for flr_rect in self.floor:
                # check if bottom is at the top of the floor rect and that the x pos is within floor area
                if self.rect.bottom >= flr_rect.top and (flr_rect.left < self.rect.center[0] < flr_rect.right):
                    bounce = True
                    break
        if bounce:
            self.speed_y = -abs(self.speed_y)   # ensure speed in y-direction is negative
        else:
            self.speed_y += 2   # apply gravity
        self.rect.y += self.speed_y

    def update(self):
        """Update the position of the fireball"""
        self.rect.x += self.speed_x
        self.apply_gravity()
        if self.active:
            self.image = self.norm_animator.get_image()
            self.check_hit_wall()
        elif self.explode_animator.is_animation_done():
            self.kill()
        else:
            self.image = self.explode_animator.get_image()


class FireBallController:
    """Manages fireballs and provides an interface for using them"""
    def __init__(self, screen, map_group, obstacles, floor, origin):
        self.screen = screen
        self.origin = origin
        self.map_group = map_group
        self.obstacles = obstacles
        self.floor = floor
        self.fireballs = Group()
        self.fb_images = [pygimg.load('map/super-mario-fireball-1'), pygimg.load('map/super-mario-fireball-2'),
                          pygimg.load('map/super-mario-fireball-3'), pygimg.load('map/super-mario-fireball-4')]
        self.exp_images = [pygimg.load('map/super-mario-fireball-explode-1'),
                           pygimg.load('map/super-mario-fireball-explode-2'),
                           pygimg.load('map/super-mario-fireball-explode-3')]

    def throw_fireball(self):
        """If there are not two fireballs already active, then throw a new fireball"""
        if len(self.fireballs) < 2:
            if self.origin.facing_right:
                n_fireball = FireBall(self.origin.rect.x + 1, self.origin.rect.topright, self.fb_images,
                                      self.exp_images, self.obstacles, self.floor)
            else:
                n_fireball = FireBall(self.origin.rect.x - 1, self.origin.rect.topleft, self.fb_images, self.exp_images,
                                      self.obstacles, self.floor, speed=-5)
            self.fireballs.add(n_fireball)
            self.map_group.add(n_fireball)

    def update_fireballs(self):
        """Update all fireballs currently in play"""
        self.fireballs.update()
        for fb in self.fireballs:
            if fb.rect.x < 0 or fb.rect.x > self.screen.get_width() or \
                    (fb.rect.y < 0 or fb.rect.y > self.screen.get_height()):
                fb.kill()
