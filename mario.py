from item import Item, FireBallController
import pygame as pg
import constants as c


class Mario(pg.sprite.Sprite):
    def __init__(self, game_objects, map_layer, map_group, screen):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = pg.image.load('images/mario_bros.png')
        if self.sprite_sheet.get_alpha():
            self.sprite_sheet = self.sprite_sheet.convert_alpha()
        else:
            self.sprite_sheet = self.sprite_sheet.convert()
            self.sprite_sheet.set_colorkey((255, 0, 255))
        self.SFX = None
        self.load_sounds()
        self.game_objects = game_objects
        self.map_layer = map_layer
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        # fireball controller allows the throwing of fireballs when possible
        self.fireball_controller = FireBallController(screen, map_group,
                                                      game_objects['collide_objs'], game_objects['floors'], self,
                                                      goomba=game_objects['goomba'], koopa=game_objects['koopa'])
        self.screen_shift = 0
        self.left_bound = 0
        self.timers = {}
        self.state_info = {}
        self.sprites_about_to_die_group = pg.sprite.Group()

        self.shell = pg.sprite.Group()

        self.right_small_normal_frames = None
        self.left_small_normal_frames = None
        self.right_small_red_frames = None
        self.left_small_red_frames = None
        self.right_small_black_frames = None
        self.left_small_black_frames = None

        self.right_big_normal_frames = None
        self.left_big_normal_frames = None
        self.right_big_red_frames = None
        self.left_big_red_frames = None
        self.right_big_black_frames = None
        self.left_big_black_frames = None

        self.right_fire_frames = None
        self.left_fire_frames = None

        self.normal_small_frames = None
        self.red_small_frames = None
        self.black_small_frames = None
        self.invincible_small_frames_list = None
        self.normal_big_frames = None
        self.red_big_frames = None
        self.black_big_frames = None
        self.fire_frames = None
        self.invincible_big_frames_list = None
        self.all_images = None
        self.right_frames = None
        self.left_frames = None

        self.frame_index = 0
        self.invincible_index = 0
        self.fire_transition_index = 0
        self.fireball_count = 0
        self.flag_pole_right = 0

        self.x_vel = None
        self.y_vel = None
        self.max_x_vel = None
        self.max_y_vel = None
        self.x_accel = None
        self.jump_vel = None
        self.gravity = None

        self.setup_timers()
        self.setup_state_booleans()
        self.setup_forces()
        self.setup_counters()
        self.load_images_from_sheet()

        self.state = c.WALK
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.key_timer = 0
        self.keybinding = {
            'action': pg.K_LSHIFT,
            'jump': pg.K_SPACE,
            'left': pg.K_LEFT,
            'right': pg.K_RIGHT,
            'down': pg.K_DOWN
        }

        self.score = 0

    def setup_timers(self):
        """Sets up timers for animations"""
        self.timers['walking'] = 0
        self.timers['invincible_animation'] = 0
        self.timers['invincible_start'] = 0
        self.timers['fire_transition'] = 0
        self.timers['death'] = 0
        self.timers['transition'] = 0
        self.timers['last_fireball'] = 0
        self.timers['hurt_invincible_1'] = 0
        self.timers['hurt_invincible_2'] = 0
        self.timers['flag_pole'] = 0

    def setup_state_booleans(self):
        """Sets up booleans that affect Mario's behavior"""
        self.state_info['facing_right'] = True
        self.state_info['allow_jump'] = True
        self.state_info['dead'] = False
        self.state_info['death_finish'] = False
        self.state_info['invincible'] = False
        self.state_info['big'] = False
        self.state_info['fire'] = False
        self.state_info['allow_fireball'] = True
        self.state_info['in_transition'] = False
        self.state_info['hurt_invincible'] = False
        self.state_info['in_castle'] = False
        self.state_info['crouching'] = False
        self.state_info['losing_invincibility'] = False

    def setup_forces(self):
        """Sets up forces that affect Mario's velocity"""
        self.x_vel = 0
        self.y_vel = 0
        self.max_x_vel = c.MAX_WALK_SPEED
        self.max_y_vel = c.MAX_Y_VEL
        self.x_accel = c.WALK_ACCEL
        self.jump_vel = c.JUMP_VEL
        self.gravity = c.GRAVITY

    def setup_counters(self):
        """These keep track of various total for important values"""
        self.frame_index = 0
        self.invincible_index = 0
        self.fire_transition_index = 0
        self.fireball_count = 0
        self.flag_pole_right = 0

    def load_sounds(self):
        """Load all Mario sound effects into a dictionary for later playback"""
        self.SFX = {
            'big_jump': pg.mixer.Sound('audio/Big-Mario-Jump.wav'),
            'coin': pg.mixer.Sound('audio/Coin.wav'),
            'small_jump': pg.mixer.Sound('audio/Small-Mario-Jump.wav'),
            'fireball': pg.mixer.Sound('audio/Fireball.wav'),
            'kick': pg.mixer.Sound('audio/Mario-Kick-Shell.wav'),
            'stomp': pg.mixer.Sound('audio/Mario-Stomp.wav'),
            'powerup': pg.mixer.Sound('audio/Get-Powerup.wav'),
            'shrink': pg.mixer.Sound('audio/Mario-Shrink.wav')
        }

    def load_images_from_sheet(self):
        """Extracts Mario images from his sprite sheet and assigns
        them to appropriate lists"""
        self.right_frames = []
        self.left_frames = []

        self.right_small_normal_frames = []
        self.left_small_normal_frames = []
        self.right_small_red_frames = []
        self.left_small_red_frames = []
        self.right_small_black_frames = []
        self.left_small_black_frames = []

        self.right_big_normal_frames = []
        self.left_big_normal_frames = []
        self.right_big_red_frames = []
        self.left_big_red_frames = []
        self.right_big_black_frames = []
        self.left_big_black_frames = []

        self.right_fire_frames = []
        self.left_fire_frames = []

        # Images for normal small mario#

        self.right_small_normal_frames.append(
            self.get_image(178, 32, 12, 16))  # Right [0]
        self.right_small_normal_frames.append(
            self.get_image(80, 32, 15, 16))  # Right walking 1 [1]
        self.right_small_normal_frames.append(
            self.get_image(96, 32, 16, 16))  # Right walking 2 [2]
        self.right_small_normal_frames.append(
            self.get_image(112, 32, 16, 16))  # Right walking 3 [3]
        self.right_small_normal_frames.append(
            self.get_image(144, 32, 16, 16))  # Right jump [4]
        self.right_small_normal_frames.append(
            self.get_image(130, 32, 14, 16))  # Right skid [5]
        self.right_small_normal_frames.append(
            self.get_image(160, 32, 15, 16))  # Death frame [6]
        self.right_small_normal_frames.append(
            self.get_image(320, 8, 16, 24))  # Transition small to big [7]
        self.right_small_normal_frames.append(
            self.get_image(241, 33, 16, 16))  # Transition big to small [8]
        self.right_small_normal_frames.append(
            self.get_image(194, 32, 12, 16))  # Frame 1 of flag pole Slide [9]
        self.right_small_normal_frames.append(
            self.get_image(210, 33, 12, 16))  # Frame 2 of flag pole slide [10]

        # Images for small mario (for invincible animation)#

        self.right_small_red_frames.append(
            self.get_image(178, 272, 12, 16))  # Right standing [0]
        self.right_small_red_frames.append(
            self.get_image(80, 272, 15, 16))  # Right walking 1 [1]
        self.right_small_red_frames.append(
            self.get_image(96, 272, 16, 16))  # Right walking 2 [2]
        self.right_small_red_frames.append(
            self.get_image(112, 272, 15, 16))  # Right walking 3 [3]
        self.right_small_red_frames.append(
            self.get_image(144, 272, 16, 16))  # Right jump [4]
        self.right_small_red_frames.append(
            self.get_image(130, 272, 14, 16))  # Right skid [5]

        # Images for small black mario (for invincible animation)#

        self.right_small_black_frames.append(
            self.get_image(178, 176, 12, 16))  # Right standing [0]
        self.right_small_black_frames.append(
            self.get_image(80, 176, 15, 16))  # Right walking 1 [1]
        self.right_small_black_frames.append(
            self.get_image(96, 176, 16, 16))  # Right walking 2 [2]
        self.right_small_black_frames.append(
            self.get_image(112, 176, 15, 16))  # Right walking 3 [3]
        self.right_small_black_frames.append(
            self.get_image(144, 176, 16, 16))  # Right jump [4]
        self.right_small_black_frames.append(
            self.get_image(130, 176, 14, 16))  # Right skid [5]

        # Images for normal big Mario

        self.right_big_normal_frames.append(
            self.get_image(176, 0, 16, 32))  # Right standing [0]
        self.right_big_normal_frames.append(
            self.get_image(81, 0, 16, 32))  # Right walking 1 [1]
        self.right_big_normal_frames.append(
            self.get_image(97, 0, 15, 32))  # Right walking 2 [2]
        self.right_big_normal_frames.append(
            self.get_image(113, 0, 15, 32))  # Right walking 3 [3]
        self.right_big_normal_frames.append(
            self.get_image(144, 0, 16, 32))  # Right jump [4]
        self.right_big_normal_frames.append(
            self.get_image(128, 0, 16, 32))  # Right skid [5]
        self.right_big_normal_frames.append(
            self.get_image(336, 0, 16, 32))  # Right throwing [6]
        self.right_big_normal_frames.append(
            self.get_image(160, 10, 16, 22))  # Right crouching [7]
        self.right_big_normal_frames.append(
            self.get_image(272, 2, 16, 29))  # Transition big to small [8]
        self.right_big_normal_frames.append(
            self.get_image(193, 2, 16, 30))  # Frame 1 of flag pole slide [9]
        self.right_big_normal_frames.append(
            self.get_image(209, 2, 16, 29))  # Frame 2 of flag pole slide [10]

        # Images for red big Mario#

        self.right_big_red_frames.append(
            self.get_image(176, 240, 16, 32))  # Right standing [0]
        self.right_big_red_frames.append(
            self.get_image(81, 240, 16, 32))  # Right walking 1 [1]
        self.right_big_red_frames.append(
            self.get_image(97, 240, 15, 32))  # Right walking 2 [2]
        self.right_big_red_frames.append(
            self.get_image(113, 240, 15, 32))  # Right walking 3 [3]
        self.right_big_red_frames.append(
            self.get_image(144, 240, 16, 32))  # Right jump [4]
        self.right_big_red_frames.append(
            self.get_image(128, 240, 16, 32))  # Right skid [5]
        self.right_big_red_frames.append(
            self.get_image(336, 240, 16, 32))  # Right throwing [6]
        self.right_big_red_frames.append(
            self.get_image(160, 250, 16, 22))  # Right crouching [7]

        # Images for black big Mario#

        self.right_big_black_frames.append(
            self.get_image(176, 144, 16, 32))  # Right standing [0]
        self.right_big_black_frames.append(
            self.get_image(81, 144, 16, 32))  # Right walking 1 [1]
        self.right_big_black_frames.append(
            self.get_image(97, 144, 15, 32))  # Right walking 2 [2]
        self.right_big_black_frames.append(
            self.get_image(113, 144, 15, 32))  # Right walking 3 [3]
        self.right_big_black_frames.append(
            self.get_image(144, 144, 16, 32))  # Right jump [4]
        self.right_big_black_frames.append(
            self.get_image(128, 144, 16, 32))  # Right skid [5]
        self.right_big_black_frames.append(
            self.get_image(336, 144, 16, 32))  # Right throwing [6]
        self.right_big_black_frames.append(
            self.get_image(160, 154, 16, 22))  # Right Crouching [7]

        # Images for Fire Mario#

        self.right_fire_frames.append(
            self.get_image(176, 48, 16, 32))  # Right standing [0]
        self.right_fire_frames.append(
            self.get_image(81, 48, 16, 32))  # Right walking 1 [1]
        self.right_fire_frames.append(
            self.get_image(97, 48, 15, 32))  # Right walking 2 [2]
        self.right_fire_frames.append(
            self.get_image(113, 48, 15, 32))  # Right walking 3 [3]
        self.right_fire_frames.append(
            self.get_image(144, 48, 16, 32))  # Right jump [4]
        self.right_fire_frames.append(
            self.get_image(128, 48, 16, 32))  # Right skid [5]
        self.right_fire_frames.append(
            self.get_image(336, 48, 16, 32))  # Right throwing [6]
        self.right_fire_frames.append(
            self.get_image(160, 58, 16, 22))  # Right crouching [7]
        self.right_fire_frames.append(
            self.get_image(0, 0, 0, 0))  # Place holder [8]
        self.right_fire_frames.append(
            self.get_image(193, 50, 16, 29))  # Frame 1 of flag pole slide [9]
        self.right_fire_frames.append(
            self.get_image(209, 50, 16, 29))  # Frame 2 of flag pole slide [10]

        # The left image frames are numbered the same as the right
        # frames but are simply reversed.

        for frame in self.right_small_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_normal_frames.append(new_image)

        for frame in self.right_small_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_red_frames.append(new_image)

        for frame in self.right_small_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_black_frames.append(new_image)

        for frame in self.right_big_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_normal_frames.append(new_image)

        for frame in self.right_big_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_red_frames.append(new_image)

        for frame in self.right_big_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_black_frames.append(new_image)

        for frame in self.right_fire_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_fire_frames.append(new_image)

        self.normal_small_frames = [self.right_small_normal_frames,
                                    self.left_small_normal_frames]

        self.red_small_frames = [self.right_small_red_frames,
                                 self.left_small_red_frames]

        self.black_small_frames = [self.right_small_black_frames,
                                   self.left_small_black_frames]

        self.invincible_small_frames_list = [self.normal_small_frames,
                                             self.red_small_frames,
                                             self.black_small_frames]

        self.normal_big_frames = [self.right_big_normal_frames,
                                  self.left_big_normal_frames]

        self.red_big_frames = [self.right_big_red_frames,
                               self.left_big_red_frames]

        self.black_big_frames = [self.right_big_black_frames,
                                 self.left_big_black_frames]

        self.fire_frames = [self.right_fire_frames,
                            self.left_fire_frames]

        self.invincible_big_frames_list = [self.normal_big_frames,
                                           self.red_big_frames,
                                           self.black_big_frames]

        self.all_images = [self.right_big_normal_frames,
                           self.right_big_black_frames,
                           self.right_big_red_frames,
                           self.right_small_normal_frames,
                           self.right_small_red_frames,
                           self.right_small_black_frames,
                           self.left_big_normal_frames,
                           self.left_big_black_frames,
                           self.left_big_red_frames,
                           self.left_small_normal_frames,
                           self.left_small_red_frames,
                           self.left_small_black_frames]

        self.right_frames = self.normal_small_frames[0]
        self.left_frames = self.normal_small_frames[1]

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width * c.SIZE_MULTIPLIER),
                                    int(rect.height * c.SIZE_MULTIPLIER)))
        return image

    def reset(self, map_layer, game_objects, reset_booleans=True):
        """Reset states back to original"""
        if reset_booleans:
            self.setup_state_booleans()
        self.state = c.WALK
        self.map_layer = map_layer
        self.game_objects = game_objects
        self.left_bound = 0
        self.screen_shift = 0

    def update(self, keys):
        """Updates Mario's states and animations once per frame"""
        self.handle_state(keys)
        if not self.state == c.DEATH_JUMP:
            self.check_for_special_state()
            self.animation()
            if self.state not in (c.SMALL_TO_BIG, c.BIG_TO_FIRE, c.BIG_TO_SMALL):
                self.check_fall()
                self.adjust_mario_position()
            if self.rect.right > self.screen_shift:
                self.screen_shift = self.rect.right + 1
                self.left_bound = self.rect.right - int(self.screen_rect.width * 0.45)
                self.map_layer.center((self.rect.centerx, self.rect.centery))
            if self.rect.top > self.screen.get_height():
                self.start_death_jump()
            self.fireball_controller.update_fireballs()

    def check_fall(self):
        """Check if falling, apply gravity if so"""
        falling = True

        for flr_rect in self.game_objects['floors']:
            if self.rect.bottom >= flr_rect.top and (flr_rect.left < self.rect.left < flr_rect.right) and \
                    not self.rect.top >= flr_rect.bottom:
                self.rect.bottom = flr_rect.top
                self.y_vel = 0
                falling = False
                break
        if falling:
            for obj in self.game_objects['collide_objs']:
                if self.rect.bottom >= obj.rect.top and (obj.rect.left < self.rect.left < obj.rect.right) and \
                        not self.rect.top >= obj.rect.bottom:
                    self.rect.bottom = obj.rect.top
                    self.y_vel = 0
                    falling = False
                    break
        if falling:
            self.state = c.JUMP     # using jump state instead of fall
            self.y_vel += c.GRAVITY
            self.frame_index = 4
        elif self.state == c.JUMP:
            self.state = c.WALK
        self.rect.y += self.y_vel

    def handle_state(self, keys):
        """Determines Mario's behavior based on his state"""
        if self.state == c.STAND:
            self.standing(keys)
        elif self.state == c.WALK:
            self.walking(keys)
        elif self.state == c.JUMP:
            self.jumping(keys)
        elif self.state == c.DEATH_JUMP:
            self.jumping_to_death()
        elif self.state == c.SMALL_TO_BIG:
            self.changing_to_big()
        elif self.state == c.BIG_TO_FIRE:
            self.changing_to_fire()
        elif self.state == c.BIG_TO_SMALL:
            self.changing_to_small()
        elif self.state == c.FLAGPOLE:
            self.flag_pole_sliding()
        elif self.state == c.BOTTOM_OF_POLE:
            self.sitting_at_bottom_of_pole()
        elif self.state == c.WALKING_TO_CASTLE:
            self.walking_to_castle()
        elif self.state == c.END_OF_LEVEL_FALL:
            self.falling_at_end_of_level()

    def standing(self, keys):
        """This function is called if Mario is standing still"""
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        self.frame_index = 0

        if keys[self.keybinding['action']]:
            if self.state_info['fire'] and self.state_info['allow_fireball']:
                self.shoot_fireball()

        if keys[self.keybinding['down']]:
            self.state_info['crouching'] = True

        if keys[self.keybinding['left']]:
            self.state_info['facing_right'] = False
            self.get_out_of_crouch()
            self.state = c.WALK
        elif keys[self.keybinding['right']]:
            self.state_info['facing_right'] = True
            self.get_out_of_crouch()
            self.state = c.WALK
        elif keys[self.keybinding['jump']]:
            if self.state_info['allow_jump']:
                if self.state_info['big']:
                    self.SFX['big_jump'].play()
                else:
                    self.SFX['small_jump'].play()
                self.state = c.JUMP
                self.y_vel = c.JUMP_VEL
                self.rect.y -= 1
        else:
            self.state = c.STAND

        if not keys[self.keybinding['down']]:
            self.get_out_of_crouch()

    def get_out_of_crouch(self):
        """Get out of crouch"""
        bottom = self.rect.bottom
        left = self.rect.x
        if self.state_info['facing_right']:
            self.image = self.right_frames[0]
        else:
            self.image = self.left_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left
        self.state_info['crouching'] = False

    def check_to_allow_jump(self, keys):
        """Check to allow Mario to jump"""
        if not keys[self.keybinding['jump']]:
            self.state_info['allow_jump'] = True

    def check_to_allow_fireball(self, keys):
        """Check to allow the shooting of a fireball"""
        if not keys[self.keybinding['action']]:
            self.state_info['allow_fireball'] = True

    def shoot_fireball(self):
        """Shoots fireball, allowing no more than two to exist at once"""
        if (pg.time.get_ticks() - self.timers['last_fireball']) > 200:
            if self.fireball_controller.throw_fireball():
                self.SFX['fireball'].play()
                self.state_info['allow_fireball'] = False
                self.timers['last_fireball'] = pg.time.get_ticks()

                self.frame_index = 6
                if self.state_info['facing_right']:
                    self.image = self.right_frames[self.frame_index]
                else:
                    self.image = self.left_frames[self.frame_index]

    def walking(self, keys):
        """This function is called when Mario is in a walking state
        It changes the frame, checks for holding down the run button,
        checks for a jump, then adjusts the state if necessary"""

        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        if self.frame_index == 0:
            self.frame_index += 1
            self.timers['walking'] = pg.time.get_ticks()
        else:
            if (pg.time.get_ticks() - self.timers['walking'] >
                    self.calculate_animation_speed()):
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 1

                self.timers['walking'] = pg.time.get_ticks()

        if keys[self.keybinding['action']]:
            self.max_x_vel = c.MAX_RUN_SPEED
            self.x_accel = c.RUN_ACCEL
            if self.state_info['fire'] and self.state_info['allow_fireball']:
                self.shoot_fireball()
        else:
            self.max_x_vel = c.MAX_WALK_SPEED
            self.x_accel = c.WALK_ACCEL

        if keys[self.keybinding['jump']]:
            if self.state_info['allow_jump']:
                if self.state_info['big']:
                    self.SFX['big_jump'].play()
                else:
                    self.SFX['small_jump'].play()
                self.state = c.JUMP
                if self.x_vel > 4.5 or self.x_vel < -4.5:
                    self.y_vel = c.JUMP_VEL - .5
                else:
                    self.y_vel = c.JUMP_VEL
                self.rect.y -= 1

        if keys[self.keybinding['left']]:
            self.get_out_of_crouch()
            self.state_info['facing_right'] = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.WALK_ACCEL

            if self.x_vel > (self.max_x_vel * -1):
                self.x_vel -= self.x_accel
                if self.x_vel > -0.5:
                    self.x_vel = -0.5
            elif self.x_vel < (self.max_x_vel * -1):
                self.x_vel += self.x_accel

        elif keys[self.keybinding['right']]:
            self.get_out_of_crouch()
            self.state_info['facing_right'] = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.WALK_ACCEL

            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel
                if self.x_vel < 0.5:
                    self.x_vel = 0.5
            elif self.x_vel > self.max_x_vel:
                self.x_vel -= self.x_accel

        else:
            if self.state_info['facing_right']:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND

    def check_left_side(self):
        """Check if Mario is toward the left side of the screen"""
        return self.rect.left <= self.left_bound

    def calculate_animation_speed(self):
        """Used to make walking animation speed be in relation to
        Mario's x-vel"""
        if self.x_vel == 0:
            animation_speed = 130
        elif self.x_vel > 0:
            animation_speed = 130 - (self.x_vel * 13)
        else:
            animation_speed = 130 - (self.x_vel * 13 * -1)

        return animation_speed

    def jumping(self, keys):
        """Called when Mario is in a JUMP state."""
        self.state_info['allow_jump'] = False
        self.frame_index = 4
        self.check_to_allow_fireball(keys)

        if keys[self.keybinding['left']]:
            if self.x_vel > (self.max_x_vel * - 1):
                self.x_vel -= self.x_accel

        elif keys[self.keybinding['right']]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel

        if keys[self.keybinding['action']]:
            if self.state_info['fire'] and self.state_info['allow_fireball']:
                self.shoot_fireball()

    def jumping_to_death(self):
        """Called when Mario is in a DEATH_JUMP state"""
        if self.timers['death'] == 0:
            self.timers['death'] = pg.time.get_ticks()
        elif (pg.time.get_ticks() - self.timers['death']) > 500:
            self.rect.y += self.y_vel
            self.y_vel += self.gravity
        if not self.state_info['death_finish'] and self.rect.y > self.screen.get_height() * 2:
            self.state_info['death_finish'] = True

    def start_death_jump(self):
        """Used to put Mario in a DEATH_JUMP state"""
        self.state_info['dead'] = True
        self.y_vel = -11
        self.x_vel = 0
        self.gravity = .5
        self.frame_index = 6
        self.right_frames = self.right_small_normal_frames
        self.image = self.right_frames[self.frame_index]
        self.state = c.DEATH_JUMP
        self.state_info['in_transition'] = True
        pg.mixer.music.stop()

    def changing_to_big(self):
        """Changes Mario's image attribute based on time while
        transitioning to big"""
        self.state_info['in_transition'] = True

        if self.timers['transition'] == 0:
            self.timers['transition'] = pg.time.get_ticks()
        elif self.timer_between_these_two_times(135, 200):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(200, 365):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(365, 430):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(430, 495):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(495, 560):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(560, 625):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(625, 690):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(690, 755):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(755, 820):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(820, 885):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(885, 950):
            self.set_mario_to_big_image()
            self.state = c.WALK
            self.state_info['in_transition'] = False
            self.timers['transition'] = 0
            self.become_big()

    def become_big(self):
        self.state_info['big'] = True
        self.right_frames = self.right_big_normal_frames
        self.left_frames = self.left_big_normal_frames
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left

    def timer_between_these_two_times(self, start_time, end_time):
        """Checks if the timer is at the right time for the action."""
        if start_time <= (pg.time.get_ticks() - self.timers['transition']) < end_time:
            return True
        return False

    def set_mario_to_middle_image(self):
        """During a change from small to big, sets mario's image to the
        transition/middle size"""
        if self.state_info['facing_right']:
            self.image = self.normal_small_frames[0][7]
        else:
            self.image = self.normal_small_frames[1][7]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def set_mario_to_big_image(self):
        """During a change from small to big, sets mario's image to big"""
        if self.state_info['facing_right']:
            self.image = self.normal_big_frames[0][0]
        else:
            self.image = self.normal_big_frames[1][0]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def set_mario_to_small_image(self):
        """During a change from small to big, sets mario's image to small"""
        if self.state_info['facing_right']:
            self.image = self.normal_small_frames[0][0]
        else:
            self.image = self.normal_small_frames[1][0]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def changing_to_fire(self):
        """Called when Mario is in a BIG_TO_FIRE state (i.e. when
        he obtains a fire flower)"""
        self.state_info['in_transition'] = True

        if self.state_info['facing_right']:
            frames = [self.right_big_normal_frames[0],
                      self.fire_frames[0][0]]
        else:
            frames = [self.left_big_normal_frames[0],
                      self.fire_frames[0][1]]

        if self.timers['fire_transition'] == 0:
            self.timers['fire_transition'] = pg.time.get_ticks()
        elif (pg.time.get_ticks() - self.timers['fire_transition']) > 65 and (
                pg.time.get_ticks() - self.timers['fire_transition']) < 130:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 195:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 260:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 325:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 390:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 455:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 520:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 585:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 650:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 715:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 780:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 845:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 910:
            self.image = frames[0]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 975:
            self.image = frames[1]
        elif (pg.time.get_ticks() - self.timers['fire_transition']) < 1040:
            self.image = frames[1]
            self.state_info['fire'] = True
            self.state_info['in_transition'] = False
            self.state = c.WALK
            self.timers['transition'] = 0

    def changing_to_small(self):
        """Mario's state and animation when he shrinks from big to small
        after colliding with an enemy"""
        self.state_info['in_transition'] = True
        self.state_info['hurt_invincible'] = True
        self.state = c.BIG_TO_SMALL

        if self.state_info['facing_right']:
            frames = [self.right_big_normal_frames[4],
                      self.right_big_normal_frames[8],
                      self.right_small_normal_frames[8]
                      ]
        else:
            frames = [self.left_big_normal_frames[4],
                      self.left_big_normal_frames[8],
                      self.left_small_normal_frames[8]
                      ]

        if self.timers['transition'] == 0:
            self.timers['transition'] = pg.time.get_ticks()
        elif (pg.time.get_ticks() - self.timers['transition']) < 265:
            self.image = frames[0]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 330:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 395:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 460:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 525:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 590:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 655:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 720:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 785:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 850:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (pg.time.get_ticks() - self.timers['transition']) < 915:
            self.image = frames[2]
            self.adjust_rect()
            self.state_info['in_transition'] = False
            self.state = c.WALK
            self.state_info['big'] = False
            self.timers['transition'] = 0
            self.timers['hurt_invincible_1'] = 0
        self.become_small()

    def adjust_rect(self):
        """Makes sure new Rect has the same bottom and left
        location as previous Rect"""
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = bottom

    def become_small(self):
        self.state_info['big'] = False
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left

    def flag_pole_sliding(self):
        """State where Mario is sliding down the flag pole"""
        self.state = c.FLAGPOLE
        self.state_info['in_transition'] = True
        self.x_vel = 0
        self.y_vel = 0
        if self.state_info['big'] and not self.state_info['fire']:
            self.right_frames = self.right_fire_frames
        elif self.state_info['big']:
            self.right_frames = self.right_big_normal_frames
        else:
            self.right_frames = self.right_small_normal_frames

        if self.timers['flag_pole'] == 0:
            self.timers['flag_pole'] = pg.time.get_ticks()
        elif self.rect.bottom < 493:
            if (pg.time.get_ticks() - self.timers['flag_pole']) < 65:
                self.image = self.right_frames[9]
            elif (pg.time.get_ticks() - self.timers['flag_pole']) < 130:
                self.image = self.right_frames[10]
            elif (pg.time.get_ticks() - self.timers['flag_pole']) >= 130:
                self.timers['flag_pole'] = pg.time.get_ticks()

            self.rect.right = self.flag_pole_right
            self.y_vel = 5
            self.rect.y += self.y_vel

            if self.rect.bottom >= 488:
                self.timers['flag_pole'] = pg.time.get_ticks()

        elif self.rect.bottom >= 493:
            self.image = self.right_frames[10]

    def sitting_at_bottom_of_pole(self):
        """State when mario is at the bottom of the flag pole"""
        if self.timers['flag_pole'] == 0:
            self.timers['flag_pole'] = pg.time.get_ticks()
            self.image = self.left_frames[10]
        elif (pg.time.get_ticks() - self.timers['flag_pole']) < 210:
            self.image = self.left_frames[10]
        else:
            self.state_info['in_transition'] = False
            if self.rect.bottom < 485:
                self.state = c.END_OF_LEVEL_FALL
            else:
                self.state = c.WALKING_TO_CASTLE

    def set_state_to_bottom_of_pole(self):
        """Sets Mario to the BOTTOM_OF_POLE state"""
        self.image = self.left_frames[9]
        right = self.rect.right
        # self.rect.bottom = 493
        self.rect.x = right
        if self.state_info['big']:
            self.rect.x -= 10
        self.timers['flag_pole'] = 0
        self.state = c.BOTTOM_OF_POLE

    def walking_to_castle(self):
        """State when Mario walks to the castle to end the level"""
        self.max_x_vel = 5
        self.x_accel = c.WALK_ACCEL

        if self.x_vel < self.max_x_vel:
            self.x_vel += self.x_accel

        if self.timers['walking'] == 0 or (pg.time.get_ticks() - self.timers['walking']) > 200:
            self.timers['walking'] = pg.time.get_ticks()

        elif (pg.time.get_ticks() - self.timers['walking']) > \
                self.calculate_animation_speed():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.timers['walking'] = pg.time.get_ticks()

    def falling_at_end_of_level(self):
        """State when Mario is falling from the flag pole base"""
        self.y_vel += c.GRAVITY

    def check_for_special_state(self):
        """Determines if Mario is invincible, Fire Mario or recently hurt"""
        self.check_if_invincible()
        self.check_if_fire()
        self.check_if_hurt_invincible()
        self.check_if_crouching()

    def check_if_invincible(self):
        if self.state_info['invincible']:
            if (pg.time.get_ticks() - self.timers['invincible_start']) < 10000:
                self.state_info['losing_invincibility'] = False
                self.change_frame_list(30)
            elif (pg.time.get_ticks() - self.timers['invincible_start']) < 12000:
                self.state_info['losing_invincibility'] = True
                self.change_frame_list(100)
            else:
                self.state_info['losing_invincibility'] = False
                self.state_info['invincible'] = False
        else:
            if self.state_info['big']:
                self.right_frames = self.invincible_big_frames_list[0][0]
                self.left_frames = self.invincible_big_frames_list[0][1]
            else:
                self.right_frames = self.invincible_small_frames_list[0][0]
                self.left_frames = self.invincible_small_frames_list[0][1]

    def change_frame_list(self, frame_switch_speed):
        if (pg.time.get_ticks() - self.timers['invincible_animation']) > frame_switch_speed:
            if self.invincible_index < (len(self.invincible_small_frames_list) - 1):
                self.invincible_index += 1
            else:
                self.invincible_index = 0

            if self.state_info['big']:
                frames = self.invincible_big_frames_list[self.invincible_index]
            else:
                frames = self.invincible_small_frames_list[self.invincible_index]

            self.right_frames = frames[0]
            self.left_frames = frames[1]

            self.timers['invincible_animation'] = pg.time.get_ticks()

    def check_if_fire(self):
        if self.state_info['fire'] and not self.state_info['invincible']:
            self.right_frames = self.fire_frames[0]
            self.left_frames = self.fire_frames[1]

    def check_if_hurt_invincible(self):
        """Check if Mario is still temporarily invincible after getting hurt"""
        if self.state_info['hurt_invincible'] and self.state != c.BIG_TO_SMALL:
            if self.timers['hurt_invincible_2'] == 0:
                self.timers['hurt_invincible_2'] = pg.time.get_ticks()
            elif (pg.time.get_ticks() - self.timers['hurt_invincible_2']) < 2000:
                self.hurt_invincible_check()
            else:
                self.state_info['hurt_invincible'] = False
                self.timers['hurt_invincible_1'] = 0
                self.timers['hurt_invincible_2'] = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)

    def hurt_invincible_check(self):
        """Makes Mario invincible on a fixed interval"""
        if self.timers['hurt_invincible_1'] == 0:
            self.timers['hurt_invincible_1'] = pg.time.get_ticks()
        elif (pg.time.get_ticks() - self.timers['hurt_invincible_1']) < 35:
            self.image.set_alpha(0)
        elif (pg.time.get_ticks() - self.timers['hurt_invincible_1']) < 70:
            self.image.set_alpha(255)
            self.timers['hurt_invincible_1'] = pg.time.get_ticks()

    def check_if_crouching(self):
        """Checks if mario is crouching"""
        if self.state_info['crouching'] and self.state_info['big']:
            bottom = self.rect.bottom
            left = self.rect.x
            if self.state_info['facing_right']:
                self.image = self.right_frames[7]
            else:
                self.image = self.left_frames[7]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.x = left

    def animation(self):
        """Adjusts Mario's image for animation"""
        if self.state == c.DEATH_JUMP \
                or self.state == c.SMALL_TO_BIG \
                or self.state == c.BIG_TO_FIRE \
                or self.state == c.BIG_TO_SMALL \
                or self.state == c.FLAGPOLE \
                or self.state == c.BOTTOM_OF_POLE \
                or self.state_info['crouching']:
            pass
        elif self.state_info['facing_right']:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def check_wall(self):
        """Check if Mario is attempting to walk through a wall"""
        for obj in self.game_objects['collide_objs']:
            pts = [obj.rect.midleft, obj.rect.midright]
            for pt in pts:
                if self.rect.collidepoint(pt):
                    print('collide obj')
                    print(obj.rect.x, obj.rect.y)
                    if obj.rect.right > self.rect.right:
                        self.rect.right = obj.rect.left
                    else:
                        self.rect.left = obj.rect.right + 1
                    return True
        return False

    def adjust_mario_position(self):
        """Adjusts Mario's position based on his x, y velocities and
        potential collisions"""
        # self.last_x_position = self.rect.right
        if not self.check_left_side() and not self.check_wall():
            self.rect.x += round(self.x_vel * 2)
        # self.rect.x += round(self.x_vel)
        self.check_mario_x_collisions()

        if not self.state_info['in_transition']:
            self.rect.y += round(self.y_vel)
            self.check_mario_y_collisions()

    def check_mario_x_collisions(self):
        """Check for collisions after Mario is moved on the x axis"""
        koopa = None
        for k in self.game_objects['koopa']:
            k_pts = [k.rect.midleft, k.rect.midright]
            for pt in k_pts:
                if self.rect.collidepoint(pt):
                    koopa = k
                    break
            if koopa:
                break
        goomba = None
        for g in self.game_objects['goomba']:
            g_pts = [g.rect.midleft, g.rect.midright]
            for pt in g_pts:
                if self.rect.collidepoint(pt):
                    goomba = g
                    break
            if goomba:
                break
        power_up = pg.sprite.spritecollideany(self, self.game_objects['items'])

        if (goomba and not goomba.player_enemy_kill) or (koopa and not koopa.player_enemy_kill):
            target = goomba or koopa
            if target not in self.sprites_about_to_die_group:
                if self.state_info['invincible']:
                    self.SFX['kick'].play()
                    self.sprites_about_to_die_group.add(target)
                    target.player_enemy_kill = True
                elif self.state_info['big']:
                    self.SFX['shrink'].play()
                    self.state_info['fire'] = False
                    self.y_vel = -1
                    self.state = c.BIG_TO_SMALL
                elif self.state_info['hurt_invincible']:
                    pass
                else:
                    self.start_death_jump()
        elif power_up and not power_up.item_type == Item.ONE_UP:
            if power_up.item_type == Item.STARMAN:
                self.state_info['invincible'] = True
                pg.mixer.music.load('audio/Star-Theme.ogg')
                pg.mixer.music.play()
                self.timers['invincible_start'] = pg.time.get_ticks()
            elif power_up.item_type == Item.MUSHROOM:
                self.SFX['powerup'].play()
                self.y_vel = -1
                self.state = c.SMALL_TO_BIG
                self.state_info['in_transition'] = True
            elif power_up.item_type == Item.FIRE_FLOWER:
                self.SFX['powerup'].play()
                if self.state_info['big'] and not self.state_info['fire']:
                    self.state = c.BIG_TO_FIRE
                    self.state_info['in_transition'] = True
                elif not self.state_info['big']:
                    self.state = c.SMALL_TO_BIG
                    self.state_info['in_transition'] = True
            power_up.kill()

    def adjust_mario_for_x_collisions(self, collider):
        """Puts Mario flush next to the collider after moving on the x axis"""
        if self.rect.x < collider.rect.x:
            self.rect.right = collider.rect.left
        else:
            self.rect.left = collider.rect.right

        self.x_vel = 0

    def check_mario_y_collisions(self):
        """Checks for collisions when Mario moves along the y-axis"""
        enemy = None
        for g in self.game_objects['goomba']:
            if self.rect.collidepoint(g.rect.midtop):
                enemy = g
                break
        if not enemy:
            for k in self.game_objects['koopa']:
                if self.rect.collidepoint(k.rect.midtop):
                    enemy = k
                    break
        if enemy and not enemy.player_enemy_kill:
            print('enemy')
            enemy.set_killed()
            self.adjust_mario_for_y_enemy_collisions(enemy)

    def check_if_enemy_on_brick(self, brick):
        """Kills enemy if on a bumped or broken brick"""
        brick.rect.y -= 5

        enemy = pg.sprite.spritecollideany(brick, self.game_objects['goomba'], self.game_objects['koopa'])

        if enemy:
            self.SFX['kick'].play()
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            if self.rect.centerx > brick.rect.centerx:
                enemy.start_death_jump('right')
            else:
                enemy.start_death_jump('left')

        brick.rect.y += 5

    def adjust_mario_for_y_ground_pipe_collisions(self, collider):
        """Mario collisions with pipes on the y-axis"""
        if collider.rect.bottom > self.rect.bottom:
            self.y_vel = 0
            self.rect.bottom = collider.rect.top
            if self.state == c.END_OF_LEVEL_FALL:
                self.state = c.WALKING_TO_CASTLE
            else:
                self.state = c.WALK
        elif collider.rect.top < self.rect.top:
            self.y_vel = 7
            self.rect.top = collider.rect.bottom
            self.state = c.FALL

    def adjust_mario_for_y_enemy_collisions(self, enemy):
        """Mario collisions with all enemies on the y-axis"""
        self.SFX['stomp'].play()
        self.rect.bottom = enemy.rect.top - 1
        self.state = c.JUMP
        self.y_vel = -7
