# main.py

import pygame
import json
import datetime
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
    recipient = 'Global'  # Destinatario por defecto
    recipient_options = ['Global', 'Jugador 1', 'Jugador 2']
    recipient_index = 0  # Índice del destinatario seleccionado

    score = 0  # Puntuación del jugador

    # Variables para el sistema de replay
    event_log = []
    start_time = pygame.time.get_ticks() / 1000  # Tiempo en segundos

    running = True
    while running:
        delta_time = clock.tick(60) / 1000  # Delta time en segundos (60 FPS)
        current_time = pygame.time.get_ticks() / 1000 - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if chat_active:
                    if event.key == pygame.K_RETURN:
                        # Enviar el mensaje de chat con el destinatario seleccionado
                        client.send_chat_message(input_text, recipient)

                        # Registrar el evento de chat en el log
                        event_log.append({
                            'type': 'chat',
                            'time': current_time,
                            'player_id': client.player_id,
                            'data': {
                                'recipient': recipient,
                                'message': input_text
                            }
                        })

                        input_text = ''
                        chat_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_TAB:
                        # Cambiar el destinatario al presionar TAB
                        recipient_index = (recipient_index + 1) % len(recipient_options)
                        recipient = recipient_options[recipient_index]
                    else:
                        input_text += event.unicode
                elif event.key == pygame.K_t:
                    # Activar el chat al presionar 'T'
                    chat_active = True

        # Actualizar la posición del jugador según la entrada de teclado
        player.handle_input(game_map, delta_time)

        # Enviar la posición del jugador al servidor
        client.send_position((player.x, player.y))

        # Registrar el evento de movimiento en el log
        event_log.append({
            'type': 'movement',
            'time': current_time,
            'player_id': client.player_id,
            'data': {'position': (player.x, player.y)}
        })

        # Procesar eventos recibidos del otro jugador
        received_events = client.get_received_events()
        for evt in received_events:
            # Ajustar el tiempo del evento
            evt['time'] = current_time
            event_log.append(evt)
        client.clear_received_events()

        # Verificar colisión con objetos
        player_rect = pygame.Rect(
            int(player.x),
            int(player.y),
            player.width,
            player.height
        )
        if game_map.check_item_collision(player_rect):
            score += 1  # Aumentar la puntuación

            # Registrar el evento de recolección de objeto en el log
            event_log.append({
                'type': 'item_collected',
                'time': current_time,
                'player_id': client.player_id,
                'data': {'item_id': game_map.last_collected_item_id}
            })

        # Dibujar el mapa centrado en la posición del jugador
        game_map.draw(screen, (player.x, player.y), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Dibujar al jugador en el centro de la pantalla
        player_screen_rect = pygame.Rect(
            int(config.SCREEN_WIDTH // 2 - player.width // 2),
            int(config.SCREEN_HEIGHT // 2 - player.height // 2),
            player.width, player.height
        )
        pygame.draw.rect(screen, (255, 0, 0), player_screen_rect)  # Jugador propio (rojo)

        # Dibujar el otro jugador
        other_position = client.get_other_player_position()
        if client.get_other_player_id() is not None:
            other_rect = pygame.Rect(
                int(other_position[0] - player.x + config.SCREEN_WIDTH // 2 - player.width // 2),
                int(other_position[1] - player.y + config.SCREEN_HEIGHT // 2 - player.height // 2),
                player.width, player.height
            )
            pygame.draw.rect(screen, (0, 0, 255), other_rect)  # Otro jugador (azul)

        # Dibujar la puntuación
        score_surface = font.render(f"Puntuación: {score}", True, (255, 255, 255))
        screen.blit(score_surface, (config.SCREEN_WIDTH - 150, 10))

        # Dibujar la caja de chat
        if chat_active:
            # Fondo para el menú desplegable
            dropdown_rect = pygame.Rect(input_box.x, input_box.y - 30, 100, 24)
            pygame.draw.rect(screen, (200, 200, 200), dropdown_rect)
            recipient_surface = font.render(recipient, True, (0, 0, 0))
            screen.blit(recipient_surface, (dropdown_rect.x + 5, dropdown_rect.y + 5))

            # Caja de texto
            pygame.draw.rect(screen, (255, 255, 255), input_box)
            txt_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        else:
            # Indicador para abrir el chat
            hint_surface = font.render("Presiona 'T' para chatear", True, (255, 255, 255))
            screen.blit(hint_surface, (10, config.SCREEN_HEIGHT - 30))

        # Dibujar los mensajes de chat recientes (últimos 7 segundos)
        y_offset = 10
        for msg in client.get_chat_messages():
            msg_surface = font.render(msg, True, (255, 255, 255))
            screen.blit(msg_surface, (10, y_offset))
            y_offset += 20

        # Actualizar la pantalla
        pygame.display.flip()

    # Al salir del juego, guardar el evento de fin de partida
    event_log.append({
        'type': 'game_end',
        'time': current_time,
        'player_id': client.player_id,
        'data': {}
    })

    # Guardar el log de eventos en un archivo JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    replay_filename = f'replay_{timestamp}.json'
    with open(replay_filename, 'w') as f:
        json.dump(event_log, f)

    pygame.quit()

def replay_game(replay_file):
    import time  # Necesario para controlar el tiempo de reproducción

    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("2D Game Replay")
    clock = pygame.time.Clock()

    # Cargar el mapa y otros recursos
    game_map = Map(width=3840, height=2160)
    font = pygame.font.Font(None, 24)
    player = Player(x=0, y=0)  # Necesario para acceder a player.width y player.height

    # Cargar el archivo de replay
    with open(replay_file, 'r') as f:
        event_log = json.load(f)

    # Inicializar variables
    start_time = pygame.time.get_ticks() / 1000
    current_event_index = 0
    player_positions = {}
    chat_messages = []
    running = True

    while running:
        delta_time = clock.tick(60) / 1000  # Delta time en segundos (60 FPS)
        current_time = pygame.time.get_ticks() / 1000 - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Procesar eventos del replay
        while (current_event_index < len(event_log) and
               event_log[current_event_index]['time'] <= current_time):
            replay_event = event_log[current_event_index]
            event_type = replay_event['type']

            if event_type == 'movement':
                player_id = replay_event['player_id']
                position = replay_event['data']['position']
                player_positions[player_id] = position
            elif event_type == 'item_collected':
                item_id = replay_event['data']['item_id']
                game_map.collect_item_by_id(item_id)
            elif event_type == 'chat':
                chat_message = f"Jugador {replay_event['player_id']}: {replay_event['data']['message']}"
                chat_messages.append((chat_message, current_time))
            elif event_type == 'game_end':
                running = False  # Termina el replay
            current_event_index += 1

        # Limpiar mensajes de chat antiguos
        chat_messages = [(msg, msg_time) for msg, msg_time in chat_messages if current_time - msg_time <= 7]

        # Dibujar el mapa
        main_player_id = 1  # Puedes cambiar esto según tus necesidades
        if main_player_id in player_positions:
            main_player_position = player_positions[main_player_id]
        else:
            main_player_position = (0, 0)

        game_map.draw(screen, main_player_position, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Dibujar los jugadores
        for player_id, position in player_positions.items():
            player_rect = pygame.Rect(
                int(position[0] - main_player_position[0] + config.SCREEN_WIDTH // 2 - player.width // 2),
                int(position[1] - main_player_position[1] + config.SCREEN_HEIGHT // 2 - player.height // 2),
                player.width, player.height
            )
            color = (255, 0, 0) if player_id == main_player_id else (0, 0, 255)
            pygame.draw.rect(screen, color, player_rect)

        # Dibujar mensajes de chat
        y_offset = 10
        for msg, _ in chat_messages:
            msg_surface = font.render(msg, True, (255, 255, 255))
            screen.blit(msg_surface, (10, y_offset))
            y_offset += 20

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    mode = input("Selecciona el modo: (1) Jugar partida, (2) Reproducir replay\n")
    if mode == '1':
        main()
    elif mode == '2':
        replay_file = input("Ingresa el nombre del archivo de replay (ejemplo: replay_20230101_123456.json):\n")
        replay_game(replay_file)
    else:
        print("Opción inválida")
