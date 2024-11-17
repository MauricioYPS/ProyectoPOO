from game_object import GameObject
import pygame
class Weapon(GameObject):
    """
    Clase base para armas.
    """
    def __init__(self, x, y, name="Basic Gun", damage=10, fire_rate=1.0, color=(255, 255, 255)):
        super().__init__(x, y, width=32, height=32)
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # Disparos por segundo
        self.color = color

    def draw(self, screen, offset_x, offset_y):
        """
        Dibuja el arma en pantalla.
        """
        pygame.draw.rect(screen, self.color, (self.x - offset_x, self.y - offset_y, self.width, self.height))

class Pistol(Weapon):
    def __init__(self, x, y):
        super().__init__(x, y, name="Pistol", damage=10, fire_rate=1.5, color=(0, 255, 0))

class Rifle(Weapon):
    def __init__(self, x, y):
        super().__init__(x, y, name="Rifle", damage=20, fire_rate=0.8, color=(0, 0, 255))

class RocketLauncher(Weapon):
    def __init__(self, x, y):
        super().__init__(x, y, name="Rocket Launcher", damage=50, fire_rate=0.5, color=(255, 0, 0))
