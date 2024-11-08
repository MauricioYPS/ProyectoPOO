import pygame

class Map:
    def __init__(self, player):
        self.player = player
        self.map_width, self.map_height = 1600, 1200
        self.background_color = (200, 200, 200)

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(self.background_color)

        camera_x = self.player.x - surface.get_width() // 2
        camera_y = self.player.y - surface.get_height() // 2

        self.player.draw(surface, camera_x, camera_y)
