# item/item.py

import pygame
import uuid

class Item:
    def __init__(self, x, y, image):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.image = image
        self.collected = False
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def collect(self):
        self.collected = True

    def draw(self, screen, offset_x, offset_y):
        if not self.collected:
            screen.blit(self.image, (self.x - offset_x, self.y - offset_y))
