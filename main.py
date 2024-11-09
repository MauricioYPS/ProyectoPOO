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
    game_map = Map(tile_size=32)
    player = Player(x=1 * game_map.tile_size, y=1 * game_map.tile_size)
    client = GameClient()
    client.connect_to_server()  # Conecta el cliente al servidor

    font = pygame.font.Font(None, 24)
    input_box = pygame.Rect(10, config.SCREEN_HEIGHT - 30, 200, 24)
    input_text = ''
    chat_active = False
    recipient = 'Global'  # Destinatario por defecto
    recipient_options = ['Global', 'Jugador 1', 'Jugador 2']
    recipient_index = 0  # Índice del destinatario seleccionado

    score = 0    # Puntuación del jugador
    health = 100  # Salud inicial del jugador
    invincible = False  # Estado de invencibilidad
    invincible_time = 0  # Tiempo restante de invencibilidad

    # Variables para el sistema de replay
    event_log = []
    start_time = pygame.time.get_ticks() / 1000  # Tiempo en segundos

    # Registrar el ID del jugador principal
    event_log.append({
        'type': 'player_info',
        'time': 0,
        'player_id': client.player_id,
        'data': {}
    })

    # Registrar las posiciones iniciales de los objetos
    initial_item_positions = game_map.get_item_positions()
    event_log.append({
        'type': 'initial_items',
        'time': 0,
        'data': initial_item_positions
    })

    # Registrar las posiciones iniciales de los enemigos
    initial_enemy_states = game_map.get_enemy_states()
    event_log.append({
        'type': 'initial_enemies',
        'time': 0,
        'data': initial_enemy_states
    })

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

        # Obtener posición del otro jugador
        other_position = client.get_other_player_position()
        other_player_id = client.get_other_player_id()

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

            # Registrar el cambio de puntuación
            event_log.append({
                'type': 'score_update',
                'time': current_time,
                'player_id': client.player_id,
                'data': {'score': score}
            })

        # Actualizar enemigos con IA mejorada
        game_map.update_enemies(delta_time, [player], [other_position])

        # Registrar el estado de los enemigos en el log
        enemy_states = game_map.get_enemy_states()
        event_log.append({
            'type': 'enemy_update',
            'time': current_time,
            'data': enemy_states
        })

        # Actualizar invencibilidad
        if invincible:
            invincible_time -= delta_time
            if invincible_time <= 0:
                invincible = False

        # Detectar colisiones con enemigos
        if not invincible:
            for enemy in game_map.enemies:
                if player_rect.colliderect(enemy.rect):
                    health -= 10  # Reducir la salud
                    invincible = True
                    invincible_time = 1.0  # 1 segundo de invencibilidad

                    # Registrar el cambio de salud
                    event_log.append({
                        'type': 'health_update',
                        'time': current_time,
                        'player_id': client.player_id,
                        'data': {'health': health}
                    })
                    break  # Evitar perder más salud en el mismo frame

        # Dibujar el mapa centrado en la posición del jugador
        game_map.draw(screen, (player.x, player.y), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Dibujar al jugador en el centro de la pantalla
        player_screen_x = int(config.SCREEN_WIDTH // 2 - player.width // 2)
        player_screen_y = int(config.SCREEN_HEIGHT // 2 - player.height // 2)
        screen.blit(player.image, (player_screen_x, player_screen_y))
        

        # Dibujar el otro jugador
        if other_player_id is not None:
            other_screen_x = int(other_position[0] - player.x + config.SCREEN_WIDTH // 2 - player.width // 2)
            other_screen_y = int(other_position[1] - player.y + config.SCREEN_HEIGHT // 2 - player.height // 2)
            screen.blit(player.image, (other_screen_x, other_screen_y))

        # Dibujar enemigos
        offset_x = int(player.x - config.SCREEN_WIDTH // 2)
        offset_y = int(player.y - config.SCREEN_HEIGHT // 2)
        for enemy in game_map.enemies:
            enemy.draw(screen, offset_x, offset_y)

        # Dibujar la puntuación
        score_surface = font.render(f"Puntuación: {score}", True, (255, 255, 255))
        screen.blit(score_surface, (config.SCREEN_WIDTH - 150, 10))

        # Dibujar la salud del jugador
        health_surface = font.render(f"Salud: {health}", True, (255, 255, 255))
        screen.blit(health_surface, (10, 30))

        # Verificar si la salud llegó a cero
        if health <= 0:
            running = False
            # Mostrar mensaje de "Game Over"
            game_over_surface = font.render("¡Game Over!", True, (255, 0, 0))
            screen.blit(game_over_surface, (config.SCREEN_WIDTH // 2 - 50, config.SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)  # Esperar 2 segundos antes de cerrar
            break

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
        y_offset = 50  # Ajustar para no sobreponer con la salud
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
    game_map = Map(tile_size=32)
    font = pygame.font.Font(None, 24)
    player = Player(x=0, y=0)  # Necesario para acceder a player.width y player.height

    # Variables para el sistema de replay
    with open(replay_file, 'r') as f:
        event_log = json.load(f)

    # Determinar el ID del jugador principal a partir del event_log
    for event in event_log:
        if event['type'] == 'player_info':
            main_player_id = event['player_id']
            break
    else:
        # Si no hay evento 'player_info', por defecto es 1
        main_player_id = 1

    start_time = pygame.time.get_ticks() / 1000
    current_event_index = 0
    player_positions = {}
    player_health = {}
    player_scores = {}
    chat_messages = []
    enemy_states = {}  # Diccionario para almacenar estados de enemigos por tiempo
    running = True

    # Inicializar variables
    # Buscar los eventos de inicialización
    for event in event_log:
        if event['type'] == 'initial_items':
            initial_item_positions = event['data']
            game_map.set_item_positions(initial_item_positions)
        elif event['type'] == 'initial_enemies':
            initial_enemy_states = event['data']
            game_map.set_enemy_states(initial_enemy_states)
        elif event['type'] == 'player_info':
            # Ya procesado anteriormente
            continue
        else:
            # Salir después de procesar los eventos iniciales
            break

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
            elif event_type == 'enemy_update':
                # Actualizar el estado de los enemigos
                enemy_states = replay_event['data']
                game_map.set_enemy_states(enemy_states)
            elif event_type == 'health_update':
                player_id = replay_event['player_id']
                health = replay_event['data']['health']
                player_health[player_id] = health
            elif event_type == 'score_update':
                player_id = replay_event['player_id']
                score = replay_event['data']['score']
                player_scores[player_id] = score
            elif event_type == 'game_end':
                running = False  # Termina el replay
            current_event_index += 1

        # Limpiar mensajes de chat antiguos
        chat_messages = [(msg, msg_time) for msg, msg_time in chat_messages if current_time - msg_time <= 7]

        # Dibujar el mapa
        if main_player_id in player_positions:
            main_player_position = player_positions[main_player_id]
        else:
            # Si no se tiene la posición del jugador principal, usar la de cualquier jugador
            if player_positions:
                main_player_position = next(iter(player_positions.values()))
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
            screen.blit(player.image, player_rect.topleft)

            # Dibujar la salud y puntuación del jugador
            if player_id in player_health:
                health = player_health[player_id]
                health_surface = font.render(f"Salud Jugador {player_id}: {health}", True, (255, 255, 255))
                screen.blit(health_surface, (10, 30 + 20 * player_id))

            if player_id in player_scores:
                score = player_scores[player_id]
                score_surface = font.render(f"Puntuación Jugador {player_id}: {score}", True, (255, 255, 255))
                screen.blit(score_surface, (config.SCREEN_WIDTH - 250, 10 + 20 * player_id))

        # Dibujar enemigos
        offset_x = int(main_player_position[0] - config.SCREEN_WIDTH // 2)
        offset_y = int(main_player_position[1] - config.SCREEN_HEIGHT // 2)
        for enemy in game_map.enemies:
            enemy.draw(screen, offset_x, offset_y)

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
