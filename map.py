import pygame

class Map:
    def __init__(self, player):
        # Color y tamaño del mapa (para esta prueba)
        self.color = (100, 100, 100)  # Color de fondo gris para distinguir
        self.width, self.height = 1600, 1200  # Tamaño del mapa, más grande que la pantalla
        self.player = player  # Referencia al jugador para centrarse en él

    def update(self):
        # Aquí puedes agregar lógica de actualización del mapa si es necesario
        pass

    def draw(self, surface):
        # Limpia la pantalla
        surface.fill((0, 0, 0))  # Fondo negro

        # Calcula el offset para centrar al jugador en la pantalla
        offset_x = self.player.rect.centerx - surface.get_width() // 2
        offset_y = self.player.rect.centery - surface.get_height() // 2

        # Dibuja el mapa con el offset aplicado
        map_rect = pygame.Rect(-offset_x, -offset_y, self.width, self.height)
        pygame.draw.rect(surface, self.color, map_rect)

        # Dibuja el jugador centrado en la pantalla
        player_pos_on_screen = (self.player.rect.x - offset_x, self.player.rect.y - offset_y)
        surface.blit(self.player.image, player_pos_on_screen)
