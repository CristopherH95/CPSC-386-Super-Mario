import pygame
from animate import Animator
from pygame.sprite import Sprite


class Enemy(Sprite):
    ENEMY_DIRECTION = 1
    ENEMY_GRAVITY = 10
    ENEMY_SPEED = 2

    def __init__(self, screen, settings, image, x, y, player, floor, block, goombas, koopas):
        super().__init__()
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.settings = settings
        self.image = image
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.left, self.rect.top = self.x, self.y
        self.player = player
        self.floor = floor
        self.block = block
        self.goombas = goombas
        self.koopas = koopas
        self.death_animation_frame = 0
        self.last_frame = 0

        """CHANGE TO -1 TO START LEFT"""
        self.ENEMY_DIRECTION = Enemy.ENEMY_DIRECTION
        self.ENEMY_SPEED = Enemy.ENEMY_SPEED
        self.ENEMY_GRAVITY = Enemy.ENEMY_GRAVITY

        # Collision flags
        self.enemy_player_collide_flag = False
        self.enemy_block_collide_flag = False
        self.enemy_goomba_collide_flag = False
        self.enemy_koopa_collide_flag = False
        self.player_enemy_kill = False
        self.block_enemy_kill = False
        self.shell_mode = False
        self.shell_enemy_kill = False

        self.dead = False
        self.stop = False

    def check_collisions(self):
        # If flag is set already, no need to check collisions again
        # Also might stops from getting multiple flags set off
        if self.enemy_player_collide_flag or self.enemy_block_collide_flag or self.enemy_goomba_collide_flag or\
                self.enemy_koopa_collide_flag:
            return True

        # Check collisions
        if self.check_player_collision() or self.check_block_collision() or self.check_friendly_collision():
            return True
        if self.check_block_collision():
            return True

    def check_player_collision(self):
        # Check collision with player
        if self.rect.colliderect(self.player.rect):
            if self.rect.top == self.player.rect.bottom:
                self.player_enemy_kill = True
                self.last_frame = pygame.time.get_ticks()
                self.shell_mode = True
            self.player.start_death_jump()
            return True

    def check_block_collision(self):
        # Check if colliding with map (i.e pipe) or dying from block
        if pygame.sprite.spritecollideany(self, self.block):
            self.enemy_block_collide_flag = True
            self.ENEMY_DIRECTION *= -1
            return True
        """NEED TO CHECK FOR IF MARIO HITS BLOCK KILLING ENEMY"""
        #     if self.rect.contains(block_rect.rect):
        #         self.ENEMY_DIRECTION = abs(self.ENEMY_DIRECTION) * -1
        #         self.enemy_block_collide_flag = True
        #         self.block_enemy_kill = True
        #         return True

    def check_friendly_collision(self):
        # Check for collisions with friendly or koopa shell
        for goomba_rect in self.goombas:
            if self.rect.colliderect(goomba_rect.rect):
                self.ENEMY_DIRECTION *= -1
                self.enemy_goomba_collide_flag = True
                return True
        if self.rect.colliderect(self.koopas.rect) and not self.koopas.shell_movement:
            self.ENEMY_DIRECTION *= -1
            self.enemy_koopa_collide_flag = True
            return True
        if self.rect.colliderect(self.koopas.rect) and self.koopas.shell_movement:
            self.shell_enemy_kill = True
            self.enemy_koopa_collide_flag = True
            return True

    def check_floor(self):
        # Returns true if at enemy on floor
        for floor_rect in self.floor:
            if self.rect.colliderect(floor_rect):
                return True

    def check_boundary(self):
        if self.rect.right <= (self.player.rect.x - (self.screen_rect.left/2)) or \
                self.rect.top <= self.screen_rect.bottom:
            return True

    def reset_parameters(self):
        self.enemy_player_collide_flag = False
        self.enemy_block_collide_flag = False
        self.enemy_goomba_collide_flag = False
        self.enemy_koopa_collide_flag = False
        self.player_enemy_kill = False
        self.block_enemy_kill = False
        self.shell_mode = True
        self.shell_enemy_kill = False
        self.dead = False
        self.stop = False
        self.ENEMY_DIRECTION = Enemy.ENEMY_DIRECTION
        self.ENEMY_SPEED = Enemy.ENEMY_SPEED
        self.ENEMY_GRAVITY = Enemy.ENEMY_GRAVITY
        self.rect.left, self.rect.top = self.x, self.y

    def blit(self):
        self.screen.blit(self.image, self.rect)


class Goomba(Enemy):
    def __init__(self, screen, settings, x, y, player, floor, block, goombas, koopas):
        self.walk_images = ['images/enemies/goomba/GoombaLeftBoot.png',
                            'images/enemies/goomba/GoombaRightBoot.png']
        self.upside_down_images = ['images/enemies/goomba/GoombaUD1.png',
                                   'images/enemies/goomba/GoombaUD2.png']
        self.crushed_images = ['images/enemies/goomba/GoombaCrushed.png']
        self.animator = Animator(self.walk_images)
        image = self.animator.get_image()
        super().__init__(screen, settings, image, x, y, player, floor, block, goombas, koopas)

    def update(self):
        self.goomba_update()

    def goomba_update(self):
        # INSERT A WAY TO STOP MOVEMENT WHEN OFF SCREEN (CHECK BOUNDARY)
        self.goomba_physics()
        self.image = self.animator.get_image()

    def goomba_physics(self):
        """USE MARIO CURRENT POSITION TO GET LEFT OF SCREEN"""
        # if self.check_boundary():
        #     self.kill()
        if self.rect.right <= self.screen_rect.left or self.rect.top >= self.screen_rect.bottom:
            print(self.rect.x, self.rect.y)
            print(self.screen_rect.left, self.screen_rect.bottom)
            print("Dead")
            self.kill()

        # If no blocks are touching enemy -> Fall Down Pit
        if not self.check_floor() and not self.stop:
            self.rect.y += (abs(self.ENEMY_DIRECTION) * self.ENEMY_GRAVITY)

        # if not self.check_collisions():
        if self.check_floor() and not self.stop:
            self.rect.x += (self.ENEMY_DIRECTION * self.ENEMY_SPEED)

        # If collision
        if self.check_collisions():
            # Collides with player
            if self.enemy_player_collide_flag:
                # Enemy dead
                if self.player_enemy_kill:
                    time = pygame.time.get_ticks()
                    # Animate and keep on screen for half a second before killing sprite
                    self.animator = Animator(self.crushed_images)
                    self.stop = True
                    if abs(self.last_frame - time) > 500:
                        self.kill()
                # Player killed so stop but animate
                else:
                    self.stop = True
                    self.rect.x += 0
            # Collision with map or block
            elif self.enemy_block_collide_flag:
                # Killed by player hitting block
                if self.block_enemy_kill:
                    time = pygame.time.get_ticks()
                    self.stop = True
                    # Animate getting hit by block (Go up for two seconds)
                    self.rect.y += (abs(self.ENEMY_DIRECTION) * self.ENEMY_SPEED)
                    # After two seconds fall down while upside down
                    if self.death_animation_frame == 0 and abs(self.last_frame - time) > 2000:
                        self.animator = Animator(self.upside_down_images)
                        self.death_animation_frame += 1
                        self.ENEMY_DIRECTION *= -1
                    """MIGHT BE REDUNDANT WITH CHECK BOUNDARY"""
                    # Kill off after 10 seconds (Enough to be off screen)
                    if abs(self.last_frame - time) > 10000:
                        self.death_animation_frame = 0
                        self.kill()
                # If colliding with map (i.e. Pipe) change direction
                else:
                    self.rect.x += (self.ENEMY_DIRECTION * self.ENEMY_SPEED)
                    self.enemy_block_collide_flag = False
            # If colliding with goomba change direction
            elif self.enemy_goomba_collide_flag:
                self.rect.x += (self.ENEMY_DIRECTION * self.ENEMY_SPEED)
                self.enemy_goomba_collide_flag = False
            # If colliding with koopa
            elif self.enemy_koopa_collide_flag:
                # Colliding with koopa shell
                if self.shell_enemy_kill:
                    # Change to upside down images and fall down
                    time = pygame.time.get_ticks()
                    if self.death_animation_frame == 0:
                        self.animator = Animator(self.upside_down_images)
                        self.death_animation_frame += 1
                    self.rect.y += abs(self.ENEMY_DIRECTION * self.ENEMY_SPEED)
                    # Kill off after 10 seconds (Enough to be off screen)
                    """MIGHT BE REDUNDANT ^ CHECKS AT TOP"""
                    if abs(self.last_frame - time) > 10000:
                        self.death_animation_frame = 0
                        self.kill()
                # Colliding with koopa enemy
                else:
                    self.rect.x += (self.ENEMY_DIRECTION * self.ENEMY_SPEED)
                    self.enemy_koopa_collide_flag = False


class Koopa(Enemy):
    def __init__(self, screen, settings, x, y, player, floor, block, goombas, koopas):
        self.left_images = ['images/enemies/koopa/KoopaWalkLeft1.png',
                            'images/enemies/koopa/KoopaWalkLeft2.png']
        self.right_images = ['images/enemies/koopa/KoopaWalkRight1.png',
                             'images/enemies/koopa/KoopaWalkRight2.png']
        self.death_images = ['images/enemies/koopa/KoopaShell.png']
        self.UD_death_images = ['images/enemies/koopa/KoopaShellUD.png']
        self.feet_images = ['images/enemies/koopa/KoopaLegs.png']
        self.animator = Animator(self.left_images)
        image = self.animator.get_image()
        super().__init__(screen, settings, image, x, y, player, floor, block, goombas, koopas)

        self.shell_movement = False
        self.collision_flag = False
        self.feet_frame = 0
        self.counter = 0

    def koopa_update(self):
        self.koopa_physics()
        self.image = self.animator.get_image()

    def check_player_shell_collision(self):
        if self.rect.colliderect(self.player.rect):
            if self.rect.x >= self.player.rect.x:
                self.ENEMY_DIRECTION = abs(self.ENEMY_DIRECTION)
            else:
                self.ENEMY_DIRECTION *= -1
            self.shell_movement = True
            return True

    def koopa_physics(self):
        """USE MARIO CURRENT POSITION TO GET LEFT OF SCREEN"""
        # if self.check_boundary():
        #     self.kill()
        if self.rect.right <= self.screen_rect.left or self.rect.top <= self.screen_rect.bottom:
            print("Dead")
            self.kill()

        # If no blocks are touching enemy -> Fall Down Pit
        if not self.check_floor() and not self.stop:
            self.rect.y += (abs(self.ENEMY_DIRECTION) * self.ENEMY_GRAVITY)

        # if not self.check_collisions():
        if self.check_floor() and not self.stop:
            self.rect.x += (self.ENEMY_DIRECTION * self.ENEMY_SPEED)

        # If collision
        if self.check_collisions():
            # Collides with player when not in shell -> Player Dies
            if self.enemy_player_collide_flag and not self.shell_mode:
                self.rect.x += 0
            # Collides with player when in shell -> Movement
            if self.enemy_player_collide_flag and self.shell_mode:
                time = pygame.time.get_ticks()
                self.animator = Animator(self.death_images)
                # Collide with player in shell mode causes movement
                if self.check_player_shell_collision():
                    self.enemy_player_collide_flag = False
                # Not being hit by player again makes koopa pop out of shell
                if not self.check_player_shell_collision() and abs(self.last_frame - time) > 8000:
                    if self.counter == 0:
                        self.animator = Animator(self.feet_images)
                        self.feet_frame = pygame.time.get_ticks()
                        self.counter += 1
                    if abs(self.feet_frame - time) > 3000:
                        self.animator = Animator(self.left_images)
                        self.enemy_player_collide_flag = False
                        self.shell_mode = False
            # Collision with map or block
            elif self.enemy_block_collide_flag:
                # Killed by player hitting block
                if self.block_enemy_kill:
                    self.animator = Animator(self.death_images)
                    time = pygame.time.get_ticks()
                    # Animate getting hit by block (Go up for two seconds)
                    # After two seconds fall down while upside down
                    self.rect.y += self.ENEMY_DIRECTION
                    if self.death_animation_frame == 0 and abs(self.last_frame - time) > 2000:
                        self.animator = Animator(self.UD_death_images)
                        self.ENEMY_DIRECTION *= -1
                        self.death_animation_frame += 1
                    # Kill off after 10 seconds (Enough to be off screen)
                    if abs(self.last_frame - time) > 10000:
                        self.death_animation_frame = 0
                        # self.kill()
                        self.stop = True
                # If colliding with map (i.e. Pipe) change direction
                if not self.block_enemy_kill:
                    self.ENEMY_DIRECTION *= -1
                    self.rect.x += 3
                    self.enemy_block_collide_flag = False

            # If colliding with goomba change direction
            elif self.enemy_goomba_collide_flag:
                self.ENEMY_DIRECTION *= -1
                self.rect.x += 3
                self.enemy_goomba_collide_flag = False

            # If colliding with koopa
            elif self.enemy_koopa_collide_flag:
                # Colliding with koopa enemy
                if not self.shell_enemy_kill:
                    self.ENEMY_DIRECTION *= -1
                    self.rect.x += 3
                    self.enemy_koopa_collide_flag = False
                # Colliding with koopa shell
                if self.shell_enemy_kill:
                    # Change to upside down images and fall down
                    time = pygame.time.get_ticks()
                    if self.death_animation_frame == 0:
                        self.animator = Animator(self.UD_death_images)
                        self.death_animation_frame += 1
                    self.rect.y += abs(self.ENEMY_DIRECTION)
                    # Kill off after 10 seconds (Enough to be off screen)
                    if abs(self.last_frame - time) > 10000:
                        self.death_animation_frame = 0
                        # self.kill()
                        self.stop = True
