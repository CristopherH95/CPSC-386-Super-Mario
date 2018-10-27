from configparser import ConfigParser
from event_loop import EventLoop
from pytmx.util_pygame import load_pygame
from block import Block, CoinBlock, QuestionBlock
from pipe import Pipe
import pygame
import pyscroll


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
        self.tmx_data = load_pygame('map/world1.tmx')    # load map data
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)   # get PyScroll map data
        self.clock = pygame.time.Clock()    # clock for limiting fps
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen.get_size(), alpha=True)  # map renderer
        self.map_group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=5)  # Sprite group for map
        self.player_spawn = self.tmx_data.get_object_by_name('player')      # get player spawn object from map data
        self.game_objects = None
        self.init_game_objects()
        self.map_center = self.map_layer.translate_point((self.player_spawn.x, self.player_spawn.y))
        self.test = TestSprite(self.map_center)   # test sprite for player location
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
        self.action_map = {pygame.KEYDOWN: self.set_cam_move, pygame.KEYUP: self.unset_cam_move}
        print(self.map_layer.view_rect.center)

    def init_game_objects(self):
        """Create all game objects in memory by extracting them from the map file"""
        self.game_objects = {
            'floors': [],
            'blocks': pygame.sprite.Group(),
            'q_blocks': pygame.sprite.Group(),
            'pipes': pygame.sprite.Group(),
            'flag': pygame.sprite.Group(),
            'win-zone': []
        }
        floor_data = self.tmx_data.get_layer_by_name('walls')
        block_data = self.tmx_data.get_layer_by_name('blocks')
        q_block_data = self.tmx_data.get_layer_by_name('q-blocks')
        pipe_data = self.tmx_data.get_layer_by_name('pipes')
        flag_data = self.tmx_data.get_layer_by_name('flag')
        for obj in floor_data:  # walls represented as pygame Rects
            self.game_objects['floors'].append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        for block in block_data:
            b_sprite = CoinBlock(block.x, block.y, block.image, self.screen, self.map_group, coins=4)
            self.map_group.add(b_sprite)    # draw using this group
            self.game_objects['blocks'].add(b_sprite)       # check collisions using this group
        for q_block in q_block_data:
            q_sprite = QuestionBlock(q_block.x, q_block.y, self.screen)
            self.map_group.add(q_sprite)    # draw using this group
            self.game_objects['q_blocks'].add(q_sprite)     # check collisions using this group
        for pipe in pipe_data:
            p_sprite = Pipe(pipe.x, pipe.y, pipe.image, self.screen)
            self.map_group.add(p_sprite)    # draw using this group
            self.game_objects['pipes'].add(p_sprite)        # check collisions using this group
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
        if self.move_flags['right']:
            self.map_center = (self.map_center[0] + self.scroll_speed, self.map_center[1])
        if self.move_flags['left']:
            self.map_center = (self.map_center[0] - self.scroll_speed, self.map_center[1])
        if self.move_flags['up']:
            self.map_center = (self.map_center[0], self.map_center[1] - self.scroll_speed)
        if self.move_flags['down']:
            self.map_center = (self.map_center[0], self.map_center[1] + self.scroll_speed)
        for block in self.game_objects['blocks']:
            block.update()
        self.map_group.center(self.map_center)
        self.test.update(self.game_objects['floors'])  # update and check if not touching any walls
        self.game_objects['q_blocks'].update()
        self.map_group.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Launch the game and begin checking for events"""
        loop = EventLoop(loop_running=True, actions=self.action_map)

        while True:
            self.clock.tick(60)     # 60 fps cap
            loop.check_events()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.run()
