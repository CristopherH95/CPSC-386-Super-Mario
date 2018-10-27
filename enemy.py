from animate import Animator
from pygame.sprite import Sprite


class Enemy(Sprite):
    ENEMY_SIZE = 32
    ENEMY_SPEED = 1

    def __init__(self, screen, settings, image, x, y, player, block, friendly):
        super().__init__()
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.settings = settings
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = x, y
        self.player = player
        self.block = block
        self.friendly = friendly

        self.SIZE = Enemy.ENEMY_SIZE
        self.ENEMY_DIRECTION = Enemy.ENEMY_SPEED * -1

        self.enemy_player_collide_flag = False
        self.enemy_block_collide_flag = False
        self.enemy_friendly_collide_flag = False

    def check_collisions(self):
        self.check_player_collision()
        self.check_block_collision()
        self.check_friendly_collision()

    def check_player_collision(self):
        if self.rect.colliderect(self.player.rect):
            self.player.enemy_player_collide_flag = True
            return True

    def check_block_collision(self):
        for block_rect in self.block:
            if self.rect.left == block_rect.rect.right:
                block_rect.enemy_block_collide_flag = True
                return True
            if self.rect.right == block_rect.rect.left:
                block_rect.enemy_block_collide_flag = True
                return True

    def check_friendly_collision(self):
        for friendly_rect in self.friendly:
            if self.rect.colliderect(friendly_rect.rect):
                friendly_rect.enemy_friendly_collide_flag = True
                return True

    def blit(self):
        self.screen.blit(self.image, self.rect)


class Goomba(Enemy):
    def __init__(self, screen, x, y, settings, player, block, friendly):
        images = ['images/enemies/GoombaLeftBoot.png',
                  'images/enemies/GoombaRightBoot.png']
        self.animator = Animator(images)
        image = self.animator.get_image()
        super().__init__(screen, settings, image, x, y, player, block, friendly)

    def goomba_update(self):
        self.image = self.animator.get_image()

    def goomba_physics(self):
        # Movement
        if not self.check_collisions():
            self.rect.x += self.ENEMY_DIRECTION

        if self.check_collisions():
            # Stop moving, with animation
            if self.enemy_player_collide_flag:
                self.rect.x += 0

            # Change Direction
            elif self.enemy_block_collide_flag:
                self.ENEMY_DIRECTION *= -1

            elif self.enemy_friendly_collide_flag:
                self.ENEMY_DIRECTION *= -1

