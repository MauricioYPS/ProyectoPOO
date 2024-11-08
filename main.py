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
    game_map = Map(width=3840, height=2160)
    player = Player(x=5 * game_map.tile_size, y=5 * game_map.tile_size)
    client = GameClient()
    client.connect_to_server()  # Conecta el cliente al servidor

    font = pygame.font.Font(None, 24)
    input_box = pygame.Rect(10, config.SCREEN_HEIGHT - 30, 200, 24)
    input_text = ''
    chat_active = False

    running = True
    while running:
        delta_time = clock.tick(60) / 1000  # Delta time en segundos (60 FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if chat_active:
                    if event.key == pygame.K_RETURN:
                        # Enviar el mensaje de chat
                        client.send_chat_message(input_text)
                        input_text = ''
                        chat_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                elif event.key == pygame.K_t:
                    # Activar el chat al presionar 'T'
                    chat_active = True

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

        # Dibujar la caja de chat
        if chat_active:
            pygame.draw.rect(screen, (255, 255, 255), input_box)
            txt_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Dibujar los mensajes de chat
        y_offset = 10
        for msg in client.get_chat_messages()[-5:]:  # Mostrar los últimos 5 mensajes
            msg_surface = font.render(msg, True, (255, 255, 255))
            screen.blit(msg_surface, (10, y_offset))
            y_offset += 20

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
