# player/player.py

import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 200  # Aumentamos la velocidad en píxeles por segundo para hacerla más notoria
        self.width = 32
        self.height = 32

    def handle_input(self, game_map, delta_time):
        """Actualiza la posición del jugador según las teclas presionadas, considerando colisiones."""
        keys = pygame.key.get_pressed()
        
        dx = dy = 0

        # Determinar la dirección del movimiento
        if keys[pygame.K_UP]:
            dy = -self.speed * delta_time
        if keys[pygame.K_DOWN]:
            dy = self.speed * delta_time
        if keys[pygame.K_LEFT]:
            dx = -self.speed * delta_time
        if keys[pygame.K_RIGHT]:
            dx = self.speed * delta_time

        # Calcular nueva posición con dx y dy y verificar si es transitable
        new_x = int(self.x + dx)
        new_y = int(self.y + dy)

        # Comprobar si el tile de destino es transitable
        if game_map.is_walkable(new_x, int(self.y)):
            self.x += dx
        if game_map.is_walkable(int(self.x), new_y):
            self.y += dy
