import pygame
from map.map_layout import MAP_LAYOUT
from game_object import GameObject
from enemy.enemy import Enemy
from item.item import Item
from barrel.barrel import Barrel
from weapon.weapon import Pistol, Rifle, RocketLauncher

class Map:
    """
    Clase que representa el mapa del juego.
    Maneja la generación de tiles, dibujo y colisiones.
    """
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.tiles = []  # Matriz de tiles
        self.enemies = []  # Lista de enemigos
        self.items = []  # Lista de ítems
        self.barrels = []  # Lista de barriles
        self.width = len(MAP_LAYOUT[0]) * tile_size
        self.height = len(MAP_LAYOUT) * tile_size

        self.generate_tiles()
        self.spawn_items()

    def generate_tiles(self):
        """
        Genera los tiles del mapa a partir de MAP_LAYOUT.
        """
        for row_index, row in enumerate(MAP_LAYOUT):
            tile_row = []
            for col_index, char in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size

                if char == "W":
                    # Crear un tile de pared
                    tile_row.append(GameObject(x, y, self.tile_size, self.tile_size))
                elif char in {"G", "E", "I", "B"}:
                    # Crear un tile transitable
                    tile_row.append(None)

                if char == "E":
                    # Generar un enemigo en esta posición
                    self.enemies.append(Enemy(x, y))
                elif char == "B":
                    # Generar un barril
                    self.barrels.append(Barrel(x, y))

            self.tiles.append(tile_row)

    def spawn_items(self):
        """
        Genera ítems en posiciones específicas del mapa.
        """
        for row_index, row in enumerate(MAP_LAYOUT):
            for col_index, char in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size

                if char == "I":
                    # Generar un ítem genérico en esta posición
                    self.items.append(Item(x, y, item_type="generic"))

    def draw(self, screen, player_position, screen_size):
        """
        Dibuja el mapa, los enemigos, los ítems y los barriles en la pantalla.
        """
        offset_x = player_position[0] - screen_size[0] // 2
        offset_y = player_position[1] - screen_size[1] // 2

        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    tile.draw(screen, offset_x, offset_y)

        # Dibujar enemigos
        for enemy in self.enemies:
            enemy.draw(screen, offset_x, offset_y)

        # Dibujar ítems
        for item in self.items:
            item.draw(screen, offset_x, offset_y)

        # Dibujar barriles
        for barrel in self.barrels:
            barrel.draw(screen, offset_x, offset_y)

    def is_walkable(self, x, y):
        """
        Verifica si una posición es transitable.
        """
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        if 0 <= tile_x < len(self.tiles[0]) and 0 <= tile_y < len(self.tiles):
            return self.tiles[tile_y][tile_x] is None  # Suelo (None) es transitable
        return False

    def check_item_collision(self, player_rect):
        """
        Verifica si el jugador colisiona con algún ítem y lo recoge.
        """
        for item in self.items:
            if player_rect.colliderect(item.get_rect()):
                self.items.remove(item)  # Eliminar el ítem del mapa
                return item  # Retornar el ítem completo, no solo el tipo
        return None

    def check_barrel_collision(self, bullet_rect):
        """
        Verifica si un disparo colisiona con algún barril y lo rompe.
        """
        for barrel in self.barrels[:]:  # Iterar sobre una copia de la lista
            if bullet_rect.colliderect(barrel.get_rect()):
                print("Colisión detectada con un barril.")
                # Generar un ítem si el barril tiene un tipo válido
                new_item = barrel.break_barrel()
                if new_item:
                    self.items.append(new_item)
                    print(f"Ítem generado: {new_item}")

                self.barrels.remove(barrel)  # Romper el barril
                return True  # Colisión detectada y manejada
        return False  # No hubo colisión


    def update_enemies(self, delta_time, player):
        """
        Actualiza la posición de los enemigos para perseguir al jugador.
        """
        for enemy in self.enemies[:]:
            if enemy.health > 0:
                enemy.move_towards_player(player, self, delta_time)
            else:
                self.enemies.remove(enemy)
