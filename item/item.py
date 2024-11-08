# item/item.py

import pygame

class Item:
    next_id = 1  # Variable de clase para asignar IDs únicos

    def __init__(self, x, y, image):
        self.x = x  # Coordenada x en el mapa
        self.y = y  # Coordenada y en el mapa
        self.image = image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.collected = False  # Estado del objeto
        self.id = Item.next_id  # Asignar un ID único al objeto
        Item.next_id += 1

    def draw(self, screen, offset_x, offset_y):
        """Dibuja el objeto en la pantalla con el desplazamiento dado."""
        if not self.collected:
            screen.blit(self.image, (self.x - offset_x, self.y - offset_y))

    def collect(self):
        """Marca el objeto como recogido."""
        self.collected = True
