# main.py

import pygame
from player.player import Player
from map.map import Map
import game_config as config
from network.client import GameClient

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("2D Game")
    clock = pygame.time.Clock()

    # Crear el mapa, el cliente y el jugador
    game_map = Map(width=2000, height=2000)
    player = Player(x=config.SCREEN_WIDTH // 2, y=config.SCREEN_HEIGHT // 2)
    client = GameClient()
    client.connect_to_server()  # Conecta el cliente al servidor

    running = True
    while running:
        delta_time = clock.tick(60) / 1000  # Delta time en segundos (60 FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar la posición del jugador según la entrada de teclado
        player.handle_input(game_map, delta_time)

        # Enviar la posición del jugador al servidor
        client.send_position((player.x, player.y))

        # Dibujar el mapa centrado en la posición del jugador
        game_map.draw(screen, (player.x, player.y), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Dibujar al jugador en el centro de la pantalla
        player_rect = pygame.Rect(
            int(config.SCREEN_WIDTH // 2 - player.width // 2),
            int(config.SCREEN_HEIGHT // 2 - player.height // 2),
            player.width, player.height
        )
        pygame.draw.rect(screen, (255, 0, 0), player_rect)  # Jugador propio (rojo)

        # Dibujar el otro jugador
        other_position = client.get_other_player_position()
        other_rect = pygame.Rect(
            int(other_position[0] - player.width // 2 - (player.x - config.SCREEN_WIDTH // 2)),
            int(other_position[1] - player.height // 2 - (player.y - config.SCREEN_HEIGHT // 2)),
            player.width, player.height
        )
        pygame.draw.rect(screen, (0, 0, 255), other_rect)  # Otro jugador (azul)

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
