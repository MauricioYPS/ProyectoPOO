from game_object import GameObject
import pygame

class Item(GameObject):
    """
    Clase base para objetos coleccionables.
    """
    def __init__(self, x, y, width=32, height=32, item_type="generic", image=None):
        super().__init__(x, y, width, height, image)
        self.item_type = item_type  # Tipo de ítem (e.g., weapon, health, etc.)
        self.image = pygame.Surface((width, height))  # Representación básica
        if item_type == "weapon":
            self.image.fill((0, 255, 0))  # Verde para armas
        elif item_type == "health":
            self.image.fill((255, 0, 0))  # Rojo para salud
        else:
            self.image.fill((200, 200, 200))  # Gris para genéricos
