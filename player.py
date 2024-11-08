import pygame

class Player:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        self.speed = 5
        self.color = (0, 255, 0)
        self.size = 20

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def draw(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, self.color, (self.x - camera_x, self.y - camera_y, self.size, self.size))
