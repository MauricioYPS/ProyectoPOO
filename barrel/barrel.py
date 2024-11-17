from game_object import GameObject
from item.item import Item
import pygame
import random
from weapon.weapon import Pistol, Rifle, RocketLauncher


class Barrel(GameObject):
    """
    Clase que representa un barril interactivo.
    """
    def __init__(self, x, y, width=32, height=32, item_type="generic", image=None):
        super().__init__(x, y, width, height, image)
        self.item_type = item_type  # Tipo de ítem que contiene
        self.image = pygame.Surface((width, height))  # Representación básica
        self.image.fill((139, 69, 19))  # Marrón para el barril

    def break_barrel(self):
        """
        Rompe el barril y genera un ítem o arma aleatoriamente.
        """
        print("Barril destruido.")
        loot = random.choice([Pistol(self.x, self.y), Rifle(self.x, self.y), RocketLauncher(self.x, self.y), None])
        if loot:
            print(f"Loot generado: {loot.name if hasattr(loot, 'name') else 'Sin nombre'}")
        return loot

