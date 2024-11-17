import pygame

class GameObject:
    """
    Clase base para todos los objetos del juego.
    """
    def __init__(self, x, y, width, height, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image  # Imagen opcional para el objeto

    def get_rect(self):
        """
        Retorna un rectángulo (pygame.Rect) que representa el área del objeto.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Dibuja el objeto en pantalla, con un desplazamiento opcional.
        """
        if self.image:
            screen.blit(self.image, (self.x - offset_x, self.y - offset_y))
        else:
            pygame.draw.rect(screen, (255, 255, 255), (self.x - offset_x, self.y - offset_y, self.width, self.height))
