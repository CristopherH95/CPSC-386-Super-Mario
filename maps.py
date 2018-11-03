from pytmx.util_pygame import load_pygame
import pyscroll


def load_world_1_1(map_file, screen):
    tmx_data = load_pygame(map_file)
    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_renderer = pyscroll.BufferedRenderer(map_data, screen.get_size(), alpha=True)  # map renderer
    map_group = pyscroll.PyscrollGroup(map_layer=map_renderer, default_layer=5)  # Sprite group for map
    return tmx_data, map_renderer, map_group

# TODO: Map #2 for underground
