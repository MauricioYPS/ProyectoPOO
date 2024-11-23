# entities/barrel.py

import pygame
import random
from entities.entity import Entity
from entities.item import Item

class Barrel(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, width=40, height=40)
        try:
            self.image = pygame.image.load("assets/barrel.png").convert_alpha()
        except pygame.error as e:
            print(f"Error al cargar la imagen del barril: {e}")
            self.image = pygame.Surface((40, 40))
            self.image.fill((139, 69, 19))  # Marrón si falla la carga de la imagen
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_broken = False

    def hit(self):
        if not self.is_broken:
            self.is_broken = True
            self.break_barrel()

    def break_barrel(self):
        print("¡El barril se ha roto!")
        # Generar un arma aleatoria
        weapon = self.generate_random_weapon()
        if weapon:
            # Colocar el arma en la posición del barril
            weapon.rect.x = self.rect.x
            weapon.rect.y = self.rect.y
            return weapon
        return None

    def generate_random_weapon(self):
        # Lista de armas disponibles
        weapons = [
            {"name": "Espada Básica", "image_path": "assets/sword.png", "type": "weapon", "effect": 10},
            {"name": "Hacha Pesada", "image_path": "assets/sword.png", "type": "weapon", "effect": 15},
            {"name": "Lanza", "image_path": "assets/potion.png", "type": "weapon", "effect": 12},
            # Añade más armas según lo desees
        ]
        selected_weapon = random.choice(weapons)
        weapon = Item(
            name=selected_weapon["name"],
            image_path=selected_weapon["image_path"],
            item_type=selected_weapon["type"],
            effect=selected_weapon["effect"]
        )
        print(f"Arma generada: {weapon.name}")
        return weapon

    def draw(self, surface, camera_x, camera_y):
        if not self.is_broken:
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
        else:
            # Opcional
            pass
