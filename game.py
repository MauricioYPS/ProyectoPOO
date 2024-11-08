import pygame
from network import Network, Chat
from player import Player
from map import Map

class Game:
    def __init__(self, server_ip, port):
        pygame.init()
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Multiplayer 2D Game")

        self.network = Network(server_ip, port)
        self.chat = Chat(self.network)
        self.running = True

        self.player = Player()
        self.map = Map(self.player)

        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    message = input("Enter message: ")
                    self.chat.send_message(message)

    def display_chat_log(self):
        for message in self.chat.chat_log[-5:]:
            print(message)

    def update(self):
        self.player.update()
        self.map.update()

    def render(self):
        self.map.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.display_chat_log()
            self.clock.tick(60)
        pygame.quit()
