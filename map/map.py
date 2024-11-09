# map/map.py

import pygame
import os
import random
from .tile import Tile
from item.item import Item
from enemy.enemy import Enemy  # Importar la clase Enemy
from .map_layout import MAP_LAYOUT  # Importar el mapa

class Map:
    def __init__(self, tile_size=32):
        """Inicializa el mapa con tiles de diferentes tipos y añade objetos y enemigos."""
        self.tile_size = tile_size

        # Validar que todas las filas en MAP_LAYOUT tengan la misma longitud
        row_length = len(MAP_LAYOUT[0])
        for row in MAP_LAYOUT:
            if len(row) != row_length:
                raise ValueError("Todas las filas en MAP_LAYOUT deben tener la misma longitud.")

        self.width = row_length * tile_size
        self.height = len(MAP_LAYOUT) * tile_size
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
    
        # Ajustar el tamaño de las imágenes al tamaño del tile
        for key in self.tile_images:
            self.tile_images[key] = pygame.transform.scale(self.tile_images[key], (tile_size, tile_size))
    
        # Cargar imagen del objeto
        try:
            self.item_image = pygame.image.load(os.path.join(assets_path, "item.png"))
            self.item_image = pygame.transform.scale(self.item_image, (tile_size // 2, tile_size // 2))
        except pygame.error as e:
            print(f"Error al cargar la imagen del objeto: {e}")
            pygame.quit()
            exit()
    
        # Cargar imagen del enemigo
        try:
            self.enemy_image = pygame.image.load(os.path.join(assets_path, "enemy.png"))
            self.enemy_image = pygame.transform.scale(self.enemy_image, (tile_size, tile_size))
        except pygame.error as e:
            print(f"Error al cargar la imagen del enemigo: {e}")
            pygame.quit()
            exit()
    
        # Crear una cuadrícula de tiles basándonos en el diseño estático del mapa
        self.tiles = []
        for row_index, row in enumerate(MAP_LAYOUT):
            tile_row = []
            for col_index, tile_type in enumerate(row):
                if tile_type == 'W':
                    walkable = False
                    image = self.tile_images['wall']
                elif tile_type == 'G':
                    walkable = True
                    image = self.tile_images['grass']
                elif tile_type == 'A':
                    walkable = False
                    image = self.tile_images['water']
                else:
                    raise ValueError(f"Tipo de tile desconocido: {tile_type}")
    
                tile = Tile(tile_type, walkable, image)
                tile_row.append(tile)
            self.tiles.append(tile_row)
    
        # Añadir objetos coleccionables al mapa
        self.items = []
        self.last_collected_item_id = None  # Para almacenar el ID del último objeto recogido
        self.spawn_items()
    
        # Añadir enemigos al mapa
        self.enemies = []
        self.spawn_enemies()

    def spawn_items(self):
        """Genera objetos coleccionables en posiciones predefinidas o aleatorias en zonas transitables."""
        for _ in range(20):  # Añade 20 objetos al mapa
            attempts = 0
            while attempts < 100:  # Evitar bucles infinitos
                x = random.randint(0, len(self.tiles[0]) - 1)
                y = random.randint(0, len(self.tiles) - 1)
                tile = self.tiles[y][x]
                if tile.walkable:
                    item_x = x * self.tile_size + (self.tile_size - self.item_image.get_width()) // 2
                    item_y = y * self.tile_size + (self.tile_size - self.item_image.get_height()) // 2
                    item = Item(item_x, item_y, self.item_image)
                    self.items.append(item)
                    break
                attempts += 1
            else:
                print("Advertencia: No se pudo colocar un objeto después de 100 intentos.")

    def set_item_positions(self, item_positions):
        """Configura los objetos coleccionables con las posiciones proporcionadas."""
        self.items = []
        for item_data in item_positions:
            item = Item(item_data['x'], item_data['y'], self.item_image)
            item.id = item_data['id']
            item.collected = item_data['collected']
            self.items.append(item)

    def get_item_positions(self):
        """Devuelve las posiciones y estados de los objetos coleccionables."""
        item_positions = []
        for item in self.items:
            item_positions.append({
                'id': item.id,
                'x': item.x,
                'y': item.y,
                'collected': item.collected
            })
        return item_positions

    def spawn_enemies(self):
        """Genera enemigos en posiciones predefinidas o aleatorias en zonas transitables."""
        for _ in range(5):  # Añade 5 enemigos al mapa
            attempts = 0
            while attempts < 100:  # Evitar bucles infinitos
                x = random.randint(0, len(self.tiles[0]) - 1)
                y = random.randint(0, len(self.tiles) - 1)
                tile = self.tiles[y][x]
                if tile.walkable:
                    enemy_x = x * self.tile_size
                    enemy_y = y * self.tile_size
                    enemy = Enemy(enemy_x, enemy_y, self.enemy_image)
                    self.enemies.append(enemy)
                    break
                attempts += 1
            else:
                print("Advertencia: No se pudo colocar un enemigo después de 100 intentos.")

    def update_enemies(self, delta_time, players, other_players_positions):
        """Actualiza el movimiento de los enemigos con IA."""
        for enemy in self.enemies:
            enemy.move_towards_player(self, delta_time, players, other_players_positions)

# map/map.py

    def draw(self, screen, player_position, screen_size):
        """Dibuja el mapa y los objetos en la pantalla, centrado en la posición del jugador."""
        
        # Calcula el desplazamiento para centrar el jugador en pantalla
        offset_x = int(player_position[0] - screen_size[0] // 2)
        offset_y = int(player_position[1] - screen_size[1] // 2)
        
        # Limitar los bordes para que el mapa no se salga de los límites
        offset_x = max(0, min(offset_x, self.width - screen_size[0]))
        offset_y = max(0, min(offset_y, self.height - screen_size[1]))

        # Dibuja solo los tiles visibles en pantalla
        start_x = max(0, offset_x // self.tile_size)
        start_y = max(0, offset_y // self.tile_size)
        end_x = min(len(self.tiles[0]), (offset_x + screen_size[0]) // self.tile_size + 1)
        end_y = min(len(self.tiles), (offset_y + screen_size[1]) // self.tile_size + 1)

        for row_index in range(start_y, end_y):
            for col_index in range(start_x, end_x):
                tile = self.tiles[row_index][col_index]
                tile_x = col_index * self.tile_size - offset_x
                tile_y = row_index * self.tile_size - offset_y

                # Asegurarse de que la imagen del tile exista
                if tile.image:
                    screen.blit(tile.image, (tile_x, tile_y))
                else:
                    color = (34, 139, 34) if tile.tile_type == "G" else (0, 0, 255) if tile.tile_type == "A" else (139, 69, 19)
                    pygame.draw.rect(screen, color, (tile_x, tile_y, self.tile_size, self.tile_size))

        # Dibujar los objetos
        for item in self.items:
            item.draw(screen, offset_x, offset_y)



        # Los enemigos se dibujan desde main.py, por lo que no es necesario dibujarlos aquí

    def is_walkable(self, x, y):
        """Devuelve True si el tile en la posición (x, y) es transitable."""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        # Comprobar que la posición está dentro de los límites del mapa
        if 0 <= tile_x < len(self.tiles[0]) and 0 <= tile_y < len(self.tiles):
            return self.tiles[tile_y][tile_x].walkable
        return False

    def check_item_collision(self, player_rect):
        """Verifica si el jugador ha recogido algún objeto."""
        for item in self.items:
            if not item.collected and player_rect.colliderect(item.rect):
                item.collect()
                self.last_collected_item_id = item.id  # Almacenar el ID del objeto recogido
                return True  # Retorna True si se recogió un objeto
        return False

    def collect_item_by_id(self, item_id):
        """Marca un objeto como recogido por su ID."""
        for item in self.items:
            if item.id == item_id:
                item.collect()
                break

    def get_enemy_states(self):
        """Devuelve el estado actual de todos los enemigos."""
        enemy_states = []
        for enemy in self.enemies:
            enemy_states.append({
                'id': enemy.id,
                'x': enemy.x,
                'y': enemy.y,
                'direction': enemy.direction
            })
        return enemy_states

    def set_enemy_states(self, enemy_states):
        """Actualiza el estado de los enemigos según los datos proporcionados."""
        self.enemies = []
        for state in enemy_states:
            enemy = Enemy(state['x'], state['y'], self.enemy_image)
            enemy.id = state['id']
            enemy.direction = state['direction']
            self.enemies.append(enemy)
