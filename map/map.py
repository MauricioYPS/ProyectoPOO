# map/map.py

import pygame
import os
from .tile import Tile

class Map:
    def __init__(self, width, height, tile_size=32):
        """Inicializa el mapa con tiles de diferentes tipos."""
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.map_surface = pygame.Surface((self.width, self.height))

        # Cargar imágenes de tiles usando rutas absolutas
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.tile_images = {}
        try:
            self.tile_images["grass"] = pygame.image.load(os.path.join(assets_path, "grass.png"))
            self.tile_images["water"] = pygame.image.load(os.path.join(assets_path, "water.png"))
            self.tile_images["wall"] = pygame.image.load(os.path.join(assets_path, "wall.png"))
        except pygame.error as e:
            print(f"Error al cargar la imagen: {e}")
            pygame.quit()
            exit()

        # Crear una cuadrícula de tiles con un patrón más lógico
        self.tiles = []
        for y in range(0, self.height, tile_size):
            row = []
            for x in range(0, self.width, tile_size):
                # Crear un diseño lógico: bordes de paredes y un área central con césped y obstáculos de agua
                if x < tile_size * 3 or x >= self.width - tile_size * 3 or y < tile_size * 3 or y >= self.height - tile_size * 3:
                    tile_type = "wall"
                    walkable = False
                elif (x // tile_size) % 5 == 0 and (y // tile_size) % 5 == 0:
                    tile_type = "water"
                    walkable = False
                else:
                    tile_type = "grass"
                    walkable = True

                tile = Tile(tile_type, walkable, image=self.tile_images[tile_type])
                row.append(tile)
            self.tiles.append(row)

    def draw(self, screen, player_position, screen_size):
        """Dibuja el mapa en la pantalla, centrado en la posición del jugador."""

        # Calcula el desplazamiento necesario para centrar el jugador en pantalla
        offset_x = int(player_position[0] - screen_size[0] // 2)
        offset_y = int(player_position[1] - screen_size[1] // 2)

        # Limita los bordes para que el mapa no se salga de los límites
        offset_x = max(0, min(offset_x, self.width - screen_size[0]))
        offset_y = max(0, min(offset_y, self.height - screen_size[1]))

        # Dibuja solo los tiles visibles en pantalla
        start_x = int(offset_x // self.tile_size)
        start_y = int(offset_y // self.tile_size)
        end_x = int((offset_x + screen_size[0]) // self.tile_size + 1)
        end_y = int((offset_y + screen_size[1]) // self.tile_size + 1)

        for row_index in range(start_y, min(end_y, len(self.tiles))):
            for col_index in range(start_x, min(end_x, len(self.tiles[row_index]))):
                tile = self.tiles[row_index][col_index]
                tile_x = col_index * self.tile_size - offset_x
                tile_y = row_index * self.tile_size - offset_y

                # Asegurarse de que la imagen del tile exista
                if tile.image:
                    screen.blit(tile.image, (tile_x, tile_y))
                else:
                    # Dibuja un rectángulo de color si falta la imagen (para depuración)
                    color = (34, 139, 34) if tile.tile_type == "grass" else (0, 0, 255) if tile.tile_type == "water" else (139, 69, 19)
                    pygame.draw.rect(screen, color, (tile_x, tile_y, self.tile_size, self.tile_size))

    def is_walkable(self, x, y):
        """Devuelve True si el tile en la posición (x, y) es transitable."""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        # Comprobar que la posición está dentro de los límites del mapa
        if 0 <= tile_x < len(self.tiles[0]) and 0 <= tile_y < len(self.tiles):
            return self.tiles[tile_y][tile_x].walkable
        return False
