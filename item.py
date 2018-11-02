from animate import Animator
from pygame.sprite import Sprite
from pygame import image as pygimg
from pygame import time
# TODO: Additional item types


class Item(Sprite):
    """Represents a generic item object in the mario game"""
    def __init__(self, x, y, image, speed, obstacles, floor, rise_from=None, animated=False):
        super(Item, self).__init__()
        if animated:
            self.animator = Animator(image)
            self.image = self.animator.get_image()
        else:
            self.animator = None
            self.image = image
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
            self.jump_speed = -self.speed
        else:
            self.jump_speed = self.speed

    def flip_direction(self):
        """Flip the direction the item is moving on the x-axis"""
        self.speed = -self.speed
        self.rect.left += self.speed

    def bounce_off_obstacles(self):
        """Check if the item has hit any obstacles which cause it to bounce the other direction"""
        hit = False
        for obs in self.obstacles:
            pts = [obs.rect.bottomleft, obs.rect.midleft,
                   obs.rect.bottomright, obs.rect.midright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    self.flip_direction()
                    hit = True
                    break
            if hit:
                break

    def fall(self):
        """If the item is not supported by any floor rects, then fall down"""
        falling = True
        for rect in self.floor:
            if self.rect.bottom >= rect.top:
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
        super(Mushroom, self).__init__(x, y, image, speed, obstacles, floor, rise_from)


class FireFlower(Item):
    """A fire flower item which can be picked up by Mario, giving the ability to throw fire balls"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('fire-flower-1.png'), pygimg.load('fire-flower-2.png'),
                  pygimg.load('fire-flower-3.png'), pygimg.load('fire-flower-4.png')]
        speed = 0
        super(FireFlower, self).__init__(x, y, images, speed, obstacles, floor, rise_from, True)


class StarMan(Item):
    """A 'star-man' item which can be picked up by Mario, causing invincibility"""
    def __init__(self, x, y, obstacles, floor, rise_from=None):
        images = [pygimg.load('starman-1.png'), pygimg.load('starman-2.png'),
                  pygimg.load('starman-3.png'), pygimg.load('starman-4.png')]
        speed = 2
        self.last_jump = time.get_ticks()
        self.jump_interval = 1000   # jump around every second
        super(StarMan, self).__init__(x, y, images, speed, obstacles, floor, rise_from, True)

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


class FireBall(Sprite):
    """A fireball which can be thrown from Mario when he is in his fire flower state"""
    pass
