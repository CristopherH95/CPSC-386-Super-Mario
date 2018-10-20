from configparser import ConfigParser
from event_loop import EventLoop
from pytmx.util_pygame import load_pygame
import pygame
import pyscroll


class Game:
    """Represents the game and its related methods for running"""
    def __init__(self):
        pygame.init()
        config = ConfigParser()
        config.read('settings.ini')
        screen_size = (int(config['screen_settings']['width']),
                       int(config['screen_settings']['height']))
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(config['game_settings']['title'])
        self.tmx_data = load_pygame('map/test1.tmx')
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.clock = pygame.time.Clock()
        self.map_layer = pyscroll.BufferedRenderer(self.map_data, self.screen.get_size(), alpha=True)
        # self.map_group = pyscroll.PyscrollGroup(map_layer=self.map_layer)
        map_center = (self.map_layer.map_rect.width / 2,
                      self.map_layer.map_rect.height / 2)
        self.map_layer.center(map_center)
        self.map_layer.zoom = 0.350
        self.test_rect = pygame.Rect(0, 0, 200, 200)

    def update(self):
        """Update the screen and any objects that require individual updates"""
        self.map_layer.draw(self.screen, self.screen.get_rect())
        # self.map_group.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Launch the game and begin checking for events"""
        loop = EventLoop(loop_running=True)

        while True:
            loop.check_events()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.run()
