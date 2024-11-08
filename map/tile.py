# map/tile.py

import pygame

class Tile:
    def __init__(self, tile_type, walkable=True, image=None):
        """Inicializa un tile con su tipo, si es transitable, y una imagen opcional."""
        self.tile_type = tile_type
        self.walkable = walkable
        self.image = image  # La imagen ya está cargada como un objeto Surface
