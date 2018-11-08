from pytmx.util_pygame import load_pygame
import pyscroll


def load_world_map(map_file, screen):
    tmx_data = load_pygame(map_file)
    map_data = pyscroll.data.TiledMapData(tmx_data)
    w, h = screen.get_size()
    map_renderer = pyscroll.BufferedRenderer(map_data, (int(w * 0.65), int(h * 0.65)))  # map renderer
    map_group = pyscroll.PyscrollGroup(map_layer=map_renderer, default_layer=5)  # Sprite group for map
    return tmx_data, map_renderer, map_group
