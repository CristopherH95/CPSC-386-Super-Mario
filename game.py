from configparser import ConfigParser
from event_loop import EventLoop
from block import Block, CoinBlock, QuestionBlock
from pipe import Pipe
from coin import Coin
from maps import load_world_map
from mario import Mario
import pygame


# test sprite
class TestSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image=None):
        super(TestSprite, self).__init__()
        if not image:
            self.image = pygame.Surface((25, 25))
            self.image.fill((255, 255, 255))
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos[0], pos[1]

    def update(self, walls):
        touched_wall = False
        for wall in walls:
            if self.rect.colliderect(wall):
                touched_wall = True
                break
        if not touched_wall:
            self.rect.bottom += 1   # test the sprite dropping to the floor


class Game:
    """Represents the game and its related methods for running"""
    def __init__(self):
        pygame.init()
        config = ConfigParser()     # parse settings file
        config.read('settings.ini')
        screen_size = (int(config['screen_settings']['width']),
                       int(config['screen_settings']['height']))
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(config['game_settings']['title'])
        self.tmx_data, self.map_layer, self.map_group = load_world_map('map/world1.tmx', self.screen)
        self.clock = pygame.time.Clock()    # clock for limiting fps
        self.player_spawn = self.tmx_data.get_object_by_name('player')      # get player spawn object from map data
        self.game_objects = None
        self.init_game_objects()
        self.map_center = self.map_layer.translate_point((self.player_spawn.x, self.player_spawn.y))
        self.test = Mario(self.game_objects['blocks'], self.game_objects['q_blocks'], self.game_objects['coins'],
                          self.game_objects['pipes'], self.game_objects['goombas'],
                          self.game_objects['koopas'], self.game_objects['items'],
                          self.game_objects['collide_objs'], self.game_objects['floors'],
                          self.map_layer, self.screen)   # test sprite for player location
        self.test.rect.x, self.test.rect.y = self.player_spawn.x, self.player_spawn.y
        self.map_layer.center(self.map_center)   # center camera
        self.map_layer.zoom = 0.725     # camera zoom
        self.map_group.add(self.test)   # add test sprite to map group
        self.scroll_speed = 250    # camera scroll speed
        # camera movement for testing
        self.move_flags = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
        # action map for event loop
        # self.action_map = {pygame.KEYDOWN: self.set_cam_move, pygame.KEYUP: self.unset_cam_move}
        self.paused = False
        print(self.map_layer.view_rect.center)

    def retrieve_map_data(self, data_layer_name):
        """Retrieve map data if it exists in the game's current map, otherwise return an empty list"""
        try:
            data = self.tmx_data.get_layer_by_name(data_layer_name)
        except ValueError:
            data = []
        return data

    def init_game_objects(self):
        """Create all game objects in memory by extracting them from the map file"""
        self.game_objects = {
            'floors': [],
            'blocks': pygame.sprite.Group(),
            'q_blocks': pygame.sprite.Group(),
            'coins': pygame.sprite.Group(),
            'pipes': pygame.sprite.Group(),
            'collide_objs': pygame.sprite.Group(),  # for checking collisions with all collide-able objects
            'flag': pygame.sprite.Group(),
            'items': pygame.sprite.Group(),
            'goombas': pygame.sprite.Group(),
            'koopas': pygame.sprite.Group(),
            'win-zone': []
        }
        floor_data = self.retrieve_map_data('walls')
        block_data = self.retrieve_map_data('blocks')
        q_block_data = self.retrieve_map_data('q-blocks')
        pipe_data = self.retrieve_map_data('pipes')
        flag_data = self.retrieve_map_data('flag')
        coin_data = self.retrieve_map_data('coins')
        for obj in floor_data:  # walls represented as pygame Rects
            self.game_objects['floors'].append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        for block in block_data:
            if 'coins' in block.properties:
                b_sprite = CoinBlock.coin_block_from_tmx_obj(block, self.screen, self.map_group)
            else:
                b_sprite = CoinBlock(block.x, block.y, block.image, self.screen, self.map_group, coins=0)
            self.map_group.add(b_sprite)    # draw using this group
            self.game_objects['blocks'].add(b_sprite)       # check collisions using this group
            self.game_objects['collide_objs'].add(b_sprite)
        for q_block in q_block_data:
            q_sprite = QuestionBlock.q_block_from_tmx_obj(q_block, self.screen, self.map_group, self.game_objects)
            self.map_group.add(q_sprite)    # draw using this group
            self.game_objects['q_blocks'].add(q_sprite)     # check collisions using this group
            self.game_objects['collide_objs'].add(q_sprite)
        for coin in coin_data:
            c_sprite = Coin(coin.x, coin.y, self.screen)
            self.map_group.add(c_sprite)
            self.game_objects['coins'].add(c_sprite)
        for pipe in pipe_data:
            p_sprite = Pipe.pipe_from_tmx_obj(pipe, self.screen)
            self.map_group.add(p_sprite)    # draw using this group
            self.game_objects['pipes'].add(p_sprite)        # check collisions using this group
            self.game_objects['collide_objs'].add(p_sprite)
        for flag_part in flag_data:
            if flag_part.image:
                f_sprite = Block(flag_part.x, flag_part.y, flag_part.image, self.screen)
                self.map_group.add(f_sprite)    # draw using this group
                self.game_objects['flag'].add(f_sprite)        # check collisions using this group
            else:
                self.game_objects['win-zone'].append(pygame.Rect(flag_part.x, flag_part.y,
                                                                 flag_part.width, flag_part.height))

    def set_cam_move(self, event):
        """Set camera movement based on key pressed"""
        key = event.key
        if key == pygame.K_RIGHT:
            self.move_flags['right'] = True
        elif key == pygame.K_LEFT:
            self.move_flags['left'] = True
        elif key == pygame.K_UP:
            self.move_flags['up'] = True
        elif key == pygame.K_DOWN:
            self.move_flags['down'] = True
        elif key == pygame.K_SPACE:     # spacebar to test coin blocks
            for block in self.game_objects['blocks']:
                block.check_hit()
            for q_block in self.game_objects['q_blocks']:
                q_block.check_hit()
        elif key == pygame.K_p:
            self.paused = not self.paused

    def unset_cam_move(self, event):
        """Unset camera movement based on key pressed"""
        key = event.key
        if key == pygame.K_RIGHT:
            self.move_flags['right'] = False
        elif key == pygame.K_LEFT:
            self.move_flags['left'] = False
        elif key == pygame.K_UP:
            self.move_flags['up'] = False
        elif key == pygame.K_DOWN:
            self.move_flags['down'] = False

    def update(self):
        """Update the screen and any objects that require individual updates"""
        if not self.paused:
            if self.move_flags['right']:
                self.map_center = (self.map_center[0] + self.scroll_speed, self.map_center[1])
            if self.move_flags['left']:
                self.map_center = (self.map_center[0] - self.scroll_speed, self.map_center[1])
            if self.move_flags['up']:
                self.map_center = (self.map_center[0], self.map_center[1] - self.scroll_speed)
            if self.move_flags['down']:
                self.map_center = (self.map_center[0], self.map_center[1] + self.scroll_speed)
            self.game_objects['blocks'].update()
            self.map_group.center(self.map_center)
            self.test.update(pygame.key.get_pressed())  # update and check if not touching any walls
            self.game_objects['q_blocks'].update()
            self.game_objects['items'].update()
            self.game_objects['coins'].update()
        self.map_group.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Launch the game and begin checking for events"""
        loop = EventLoop(loop_running=True)

        while True:
            self.clock.tick(60)     # 60 fps cap
            loop.check_events()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.run()
