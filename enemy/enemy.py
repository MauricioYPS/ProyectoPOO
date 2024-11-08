# enemy/enemy.py

import pygame
import random
import math

class Enemy:
    next_id = 1  # Variable de clase para asignar IDs únicos a los enemigos

    def __init__(self, x, y, image, speed=100):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.speed = speed  # Velocidad en píxeles por segundo
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.id = Enemy.next_id  # Asignar un ID único al enemigo
        Enemy.next_id += 1

    def move_towards_player(self, game_map, delta_time, players, other_players_positions):
        """Mueve al enemigo hacia el jugador más cercano."""
        # Lista de posiciones de jugadores
        player_positions = [ (player.x, player.y) for player in players ]
        # Añadir posiciones de otros jugadores
        for pos in other_players_positions:
            if pos is not None:
                player_positions.append(pos)

        if not player_positions:
            return  # No hay jugadores, no se mueve

        # Encontrar al jugador más cercano
        closest_player_pos = min(player_positions, key=lambda pos: self.distance_to(pos))

        dx = closest_player_pos[0] - self.x
        dy = closest_player_pos[1] - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return  # Ya está en la posición del jugador

        # Calcular movimiento
        move_x = (dx / distance) * self.speed * delta_time
        move_y = (dy / distance) * self.speed * delta_time

        # Verificar colisiones con el mapa
        new_x = self.x + move_x
        new_y = self.y + move_y

        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            # Cambiar de dirección al chocar
            self.change_direction()

        self.rect.topleft = (self.x, self.y)

    def distance_to(self, position):
        """Calcula la distancia al punto dado."""
        dx = position[0] - self.x
        dy = position[1] - self.y
        return math.hypot(dx, dy)

    def change_direction(self):
        """Cambia la dirección del enemigo aleatoriamente."""
        self.direction = random.choice(['up', 'down', 'left', 'right'])

    def draw(self, screen, offset_x, offset_y):
        """Dibuja al enemigo en la pantalla con el desplazamiento dado."""
        screen.blit(self.image, (self.x - offset_x, self.y - offset_y))
