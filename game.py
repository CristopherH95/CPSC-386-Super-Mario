from configparser import ConfigParser
from event_loop import EventLoop
from pytmx.util_pygame import load_pygame
import pygame
import pyscroll


# test sprite
class TestSprite(pygame.sprite.Sprite):
    def __init__(self, map_center, spawn, image=None):
        super(TestSprite, self).__init__()
        if not image:
            self.image = pygame.Surface((25, 25))
            self.image.fill((255, 255, 255))
            self.rect = pygame.Rect(map_center[0], map_center[1], spawn.width, spawn.height)
        else:
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.left, self.rect.top = map_center[0], map_center[1]

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
        self.tmx_data = load_pygame('map/test1.tmx')    # load map data
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)   # get PyScroll map data
        self.clock = pygame.time.Clock()    # clock for limiting fps
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen.get_size(), alpha=True)  # map renderer
        self.map_group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=5)  # Sprite group for map
        self.player_spawn = self.tmx_data.get_object_by_name('player')      # get player spawn object from map data
        floor_data = self.tmx_data.get_layer_by_name('walls')
        block_data = self.tmx_data.get_layer_by_name('blocks')
        test_img = None
        for block in block_data:
            test_img = block.image
        self.walls = []
        for obj in floor_data:  # walls represented as pygame Rects
            self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        self.map_center = self.map_layer.translate_point((self.player_spawn.x, self.player_spawn.y))
        self.test = TestSprite(self.map_center, self.player_spawn, image=test_img)   # test sprite for player location
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
        self.last_update = 0
        self.action_map = {pygame.KEYDOWN: self.set_cam_move, pygame.KEYUP: self.unset_cam_move}
        print(self.map_layer.view_rect.center)

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
        self.map_group.center(self.map_center)
        self.test.update(self.walls)  # update and check if not touching any walls
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
