import pygame
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
        self.death_animation_frame = 0
        self.last_frame = 0

        # self.SIZE = Enemy.ENEMY_SIZE
        self.ENEMY_DIRECTION = Enemy.ENEMY_SPEED * -1

        self.enemy_player_collide_flag = False
        self.enemy_block_collide_flag = False
        self.enemy_friendly_collide_flag = False
        self.enemy_dead = False

    def check_collisions(self):
        if self.check_player_collision() or self.check_block_collision() or self.check_friendly_collision():
            return True

    def check_player_collision(self):
        if self.rect.colliderect(self.player.rect):
            if self.rect.top == self.player.rect.bottom:
                self.enemy_dead = True
                self.last_frame = pygame.time.get_ticks()
                return True
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
        self.death_images = ['images/enemies/GoombaCrushed.png']
        self.animator = Animator(images)
        image = self.animator.get_image()
        super().__init__(screen, settings, image, x, y, player, block, friendly)

    def goomba_update(self):
        self.image = self.animator.get_image()
        self.goomba_physics()

    def goomba_physics(self):
        # Movement
        if not self.check_collisions():
            self.rect.x += self.ENEMY_DIRECTION

        if self.check_collisions():
            # Stop moving, with animation
            if self.enemy_player_collide_flag:
                if self.enemy_dead:
                    time = pygame.time.get_ticks()
                    # Animate and keep on screen for half a second before killing sprite
                    if self.death_animation_frame == 0:
                        self.animator = Animator(self.death_images)
                        self.death_animation_frame += 1
                    if abs(self.last_frame - time) > 500:
                        self.death_animation_frame = 0
                        self.kill()
                else:
                    self.rect.x += 0

            # Change Direction and stop them from getting stuck
            elif self.enemy_block_collide_flag:
                self.ENEMY_DIRECTION *= -1
                self.rect.x += 3
                self.enemy_block_collide_flag = False

            elif self.enemy_friendly_collide_flag:
                self.ENEMY_DIRECTION *= -1
                self.rect.x += 3
                self.enemy_friendly_collide_flag = False

