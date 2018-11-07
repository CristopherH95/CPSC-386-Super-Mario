from configparser import ConfigParser
from event_loop import EventLoop
from block import Block, CoinBlock, QuestionBlock
from pipe import Pipe
from coin import Coin
from maps import load_world_map
from mario import Mario
from enemy import Goomba, Koopa
from title import Menu
from game_stats import GameStats
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
        print(str(self.rect.x))
        self.rect.x += 3
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
        self.stats = GameStats(self.screen)
        pygame.display.set_caption(config['game_settings']['title'])
        self.clock = pygame.time.Clock()    # clock for limiting fps
        self.game_objects = None
        self.tmx_data = None
        self.map_layer = None
        self.map_group = None
        self.player_spawn = None
        self.map_center = None
        self.test = None
        self.timer = 400
        self.last_tick = 0
        self.init_world_1()
        self.map_center = self.map_layer.translate_point((self.player_spawn.x, self.player_spawn.y))
        self.test = Mario(self.game_objects, self.map_layer, self.screen)   # test sprite for player location
        self.prep_enemies()
        self.test.rect.x, self.test.rect.y = self.player_spawn.x, self.player_spawn.y
        self.map_layer.center(self.map_center)   # center camera
        self.map_layer.zoom = 0.725     # camera zoom
        self.map_group.add(self.test)   # add test sprite to map group
        self.paused = False
        # print(self.map_layer.view_rect.center)
        # action map for event loop
        self.paused = False
        self.game_active = False
        self.menu = Menu(self.screen)
        print(self.map_layer.view_rect.center)

    def retrieve_map_data(self, data_layer_name):
        """Retrieve map data if it exists in the game's current map, otherwise return an empty list"""
        try:
            data = self.tmx_data.get_layer_by_name(data_layer_name)
        except ValueError:
            data = []
        return data

    def init_world_1(self):
        """Load the initial world for the game"""
        self.tmx_data, self.map_layer, self.map_group = load_world_map('map/world1.tmx', self.screen)
        self.player_spawn = self.tmx_data.get_object_by_name('player')  # get player spawn object from map data
        self.init_game_objects()
        self.map_center = self.map_layer.translate_point((self.player_spawn.x, self.player_spawn.y))

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
            'koopa': pygame.sprite.Group(),
            'goomba': pygame.sprite.Group(),
            'win-zone': []
        }
        floor_data = self.tmx_data.get_layer_by_name('walls')
        block_data = self.tmx_data.get_layer_by_name('blocks')
        q_block_data = self.tmx_data.get_layer_by_name('q-blocks')
        pipe_data = self.tmx_data.get_layer_by_name('pipes')
        coin_data = self.retrieve_map_data('coins')
        flag_data = self.tmx_data.get_layer_by_name('flag')
        # enemy_spawn_data = self.tmx_data.get_layer_by_name('enemy-spawns')
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

    def prep_enemies(self):
        """Prepare the enemy sprites"""
        # may not be necessary if passing game_objects dictionary as a whole
        #  to Mario instead of passing individual groups
        enemy_spawn_data = self.tmx_data.get_layer_by_name('enemy-spawns')
        for spawn in enemy_spawn_data:
            if spawn.properties.get('e_type', 'goomba'):
                enemy = Goomba(self.screen, None, spawn.x, spawn.y, self.test,
                               self.game_objects['floors'], self.game_objects['collide_objs'],
                               self.game_objects['goomba'], self.game_objects['koopa'])
                self.game_objects['goomba'].add(enemy)
            else:
                enemy = Koopa(self.screen, None, spawn.x, spawn.y, self.test,
                              self.game_objects['floors'], self.game_objects['collide_objs'],
                              self.game_objects['goomba'], self.game_objects['koopa'])
            self.map_group.add(enemy)
            enemy.rect.y += 23

    def update(self):
        """Update the screen and any objects that require individual updates"""
        if not self.paused and self.game_active:
            for block in self.game_objects['blocks']:
                block.check_hit(other=self.test)
            for q_block in self.game_objects['q_blocks']:
                q_block.check_hit(other=self.test)
            self.game_objects['blocks'].update()
            self.test.update(pygame.key.get_pressed())  # update and check if not touching any walls
            self.game_objects['q_blocks'].update()
            self.game_objects['items'].update()
            self.game_objects['coins'].update()
            self.game_objects['goomba'].update()
        self.map_group.draw(self.screen)
        if not self.game_active:
            self.menu.blit()
        if self.game_active:
            self.stats.blit()
            time = pygame.time.get_ticks()
            if time - self.last_tick > 600 and self.timer is not 0:
                self.last_tick = time
                self.timer -= 1
            self.stats.update(str(0), str(0), str('1-1'), str(self.timer), str(0))
        pygame.display.flip()

    def run(self):
        """Run the application loop so that the menu can be displayed and the game started"""
        loop = EventLoop(loop_running=True, actions=self.menu.action_map)

        while True:
            loop.check_events()
            self.update()
            if self.menu.start:
                self.game_active = True
                self.start_game()
                self.menu.start = False
                self.game_active = False
                self.init_world_1()

    def start_game(self):
        """Launch the game and begin checking for events"""
        loop = EventLoop(loop_running=True)

        while loop.loop_running:
            self.clock.tick(60)     # 60 fps cap
            loop.check_events()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.run()
