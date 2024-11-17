from game_object import GameObject
import pygame

class Enemy(GameObject):
    """
    Clase que representa a un enemigo.
    """
    def __init__(self, x, y, width=32, height=32, speed=50, health=50, image=None):
        super().__init__(x, y, width, height, image)
        self.speed = speed  # Velocidad reducida para enemigos
        self.health = health  # Vida inicial del enemigo
        self.image = pygame.Surface((width, height))  # Representación básica
        self.image.fill((0, 0, 255))  # Azul para distinguir a los enemigos
        self.rect = pygame.Rect(x, y, width, height)  # Rectángulo para colisiones

    def move_towards_player(self, player, game_map, delta_time):
        """
        Movimiento básico hacia el jugador, respetando colisiones con paredes.
        """
        direction_x = player.x - self.x
        direction_y = player.y - self.y
        distance = (direction_x**2 + direction_y**2)**0.5

        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        new_x = self.x + direction_x * self.speed * delta_time
        new_y = self.y + direction_y * self.speed * delta_time

        # Verificar colisiones con el mapa
        if game_map.is_walkable(new_x, self.y):
            self.x = new_x
        if game_map.is_walkable(self.x, new_y):
            self.y = new_y

        # Actualizar el rectángulo
        self.rect.topleft = (self.x, self.y)

    def receive_damage(self, amount):
        """
        Reduce la vida del enemigo.
        """
        self.health -= amount
        if self.health <= 0:
            return True  # El enemigo está muerto
        return False

    def draw(self, screen, offset_x, offset_y):
        """
        Dibuja al enemigo en la pantalla y su barra de vida.
        """
        # Dibuja al enemigo
        screen.blit(self.image, (self.x - offset_x, self.y - offset_y))

        # Dibuja la barra de vida sobre el enemigo
        life_percentage = max(self.health / 50, 0)  # Vida máxima = 50
        bar_width = self.width
        bar_height = 5
        bar_x = self.x - offset_x
        bar_y = self.y - offset_y - bar_height - 2  # Justo encima del enemigo
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # Barra roja completa
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * life_percentage, bar_height))  # Barra verde proporcional
