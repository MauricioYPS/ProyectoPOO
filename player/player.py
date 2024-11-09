# player/player.py

import pygame
import os

class Player:
    def __init__(self, x=0, y=0, speed=200):
        self.x = x
        self.y = y
        self.speed = speed  # Velocidad en píxeles por segundo
        assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
        try:
            self.image = pygame.image.load(os.path.join(assets_path, "player.png"))
            self.image = pygame.transform.scale(self.image, (32, 32))  # Ajustar al tamaño deseado
        except pygame.error as e:
            print(f"Error al cargar la imagen del jugador: {e}")
            pygame.quit()
            exit()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def handle_input(self, game_map, delta_time):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -self.speed * delta_time
        if keys[pygame.K_s]:
            dy = self.speed * delta_time
        if keys[pygame.K_a]:
            dx = -self.speed * delta_time
        if keys[pygame.K_d]:
            dx = self.speed * delta_time

        new_x = self.x + dx
        new_y = self.y + dy

        # Verificar colisiones con el mapa
        if game_map.is_walkable(new_x, self.y):
            self.x = new_x
        if game_map.is_walkable(self.x, new_y):
            self.y = new_y
