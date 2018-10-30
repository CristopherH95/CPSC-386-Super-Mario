from pygame.sprite import Sprite
# TODO: Additional item types


class Item(Sprite):
    """Represents a generic item object in the mario game"""
    def __init__(self, x, y, image, screen, speed, obstacles, floor):
        super(Item, self).__init__()
        self.image = image
        self.screen = screen
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.speed = speed
        self.jump_speed = 0
        self.obstacles = obstacles  # objects that the item may collide with
        self.floor = floor      # rects for the floor

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
            pts = [obs.rect.bottomleft, obs.rect.topleft, obs.rect.midleft,
                   obs.rect.bottomright, obs.rect.midright, obs.rect.topright]
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
            if self.rect.bottom == rect.top:
                falling = False
                break
        if falling:
            self.rect.bottom += abs(self.speed)

    def update(self):
        """Update the item position based on its speed variables"""
        if abs(self.jump_speed) > 0:
            self.rect.top += self.jump_speed
            self.jump_speed += 1    # simulate gravity reducing speed
        self.rect.left += self.speed
        self.bounce_off_obstacles()
        self.fall()
