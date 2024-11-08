import pygame

class Player:
    def __init__(self, x=400, y=300, speed=5):
        # Inicialización del jugador
        self.image = pygame.Surface((50, 50))  # Crear un rectángulo como placeholder
        self.image.fill((0, 255, 0))  # Color verde para el jugador
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed  # Velocidad de movimiento

    def handle_input(self):
        # Captura de entrada para el movimiento
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def update(self):
        # Actualización del jugador (movimiento, etc.)
        self.handle_input()  # Maneja la entrada del teclado para mover al jugador

    def draw(self, surface):
        # Dibuja al jugador en la pantalla
        surface.blit(self.image, self.rect)
