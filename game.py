import pygame
from network import Network, Chat  # Asegúrate de tener el módulo network.py configurado
from player import Player
from map import Map

class Game:
    def __init__(self, server_ip, port):
        # Inicialización de Pygame
        pygame.init()
        self.screen_width, self.screen_height = 800, 600  # Tamaño de la ventana de juego
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Multiplayer 2D Game")

        # Inicialización de la red y el chat
        self.network = Network(server_ip, port)
        self.chat = Chat(self.network)  # Pasamos self.network al chat
        self.running = True
        
        # Jugador y mapa
        self.player = Player()  # Inicializa el jugador
        self.map = Map(self.player)  # El mapa depende del jugador para centrarse en él

        # Control del juego
        self.clock = pygame.time.Clock()
        self.running = True  # Controla el bucle del juego

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN:  # Enviar mensaje con Enter
                    message = input("Enter message: ")  # Pedir el mensaje
                    self.chat.send_message(message)  # Enviar mensaje
                
    def display_chat_log(self): 
        # Muestra el log de chat en consola (temporalmente)
        for message in self.chat.chat_log[-5:]:  # Mostrar últimos 5 mensajes
            print(message)
                
                

    def update(self):
        # Actualizar lógica del juego (jugador, mapa, etc.)
        self.player.update()  # Llama al método de actualización del jugador
        self.map.update()     # Llama al método de actualización del mapa

    def render(self):
        # Dibujar el mapa y el jugador
        self.map.draw(self.screen)   # Llama a Map para que dibuje tanto el mapa como el jugador
        pygame.display.flip()  # Actualiza la pantalla

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.display_chat_log()  # Mostrar log de chat
            self.clock.tick(60)
        pygame.quit()


