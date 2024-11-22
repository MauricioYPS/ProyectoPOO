# entities/item.py

import pygame

class Item:
    def __init__(self, name, image_path, item_type, effect=None):
        self.name = name
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.type = item_type  # Por ejemplo, 'potion', 'weapon', etc.
        self.effect = effect  # Valor que define el efecto del ítem
        self.item_id = None  # Se asignará al recibir la información del servidor

    def apply_effect(self, player):
        if self.type == 'potion' and self.effect:
            # Aplicar efecto de curación
            player.health = min(player.max_health, player.health + self.effect)
            print(f"{player.name} ha recuperado {self.effect} de salud.")
        elif self.type == 'weapon':
            # Cambiar arma del jugador
            player.weapon = self
            player.update_image()
            print(f"{player.name} ha equipado {self.name}.")
        # Añadir más tipos y efectos según sea necesario
