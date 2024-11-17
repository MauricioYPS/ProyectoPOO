import pygame
from map.map import Map
from player.player import Player
from network.client import GameClient  # Asegúrate de que el cliente esté en la carpeta network
import game_config as config

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Label Shooter")
    clock = pygame.time.Clock()

    # Crear el mapa, el jugador y el cliente
    game_map = Map(tile_size=32)
    player = Player(x=100, y=100)
    client = GameClient(host="192.168.1.5", port=12345)
    client.connect_to_server()

    font = pygame.font.Font(None, 24)

    running = True
    while running:
        delta_time = clock.tick(60) / 1000  # Delta time en segundos (60 FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botón izquierdo del mouse
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    target_x = mouse_x + player.x - config.SCREEN_WIDTH // 2
                    target_y = mouse_y + player.y - config.SCREEN_HEIGHT // 2
                    player.shoot(target_x, target_y)

        # Actualizar la posición del jugador
        player.handle_input(game_map, delta_time)

        # Actualizar invulnerabilidad del jugador
        player.update_invincibility(delta_time)

        # Verificar colisiones con enemigos
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        for enemy in game_map.enemies[:]:
            if player_rect.colliderect(enemy.rect):
                player.receive_damage(10)

        # Verificar colisiones con ítems
        collected_item = game_map.check_item_collision(player_rect)
        if collected_item:
            player.pick_up_weapon(collected_item)  # Recoger el arma o ítem

        # Actualizar enemigos
        game_map.update_enemies(delta_time, player)

        # Actualizar balas del jugador
        player.update_bullets(delta_time, game_map)

        # Enviar la posición del jugador al servidor
        client.send_position(player.x, player.y)

        # Dibujar todo en pantalla
        screen.fill((0, 0, 0))  # Fondo negro
        game_map.draw(screen, (player.x, player.y), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Dibujar al jugador en el centro de la pantalla
        player_screen_x = int(config.SCREEN_WIDTH // 2 - player.width // 2)
        player_screen_y = int(config.SCREEN_HEIGHT // 2 - player.height // 2)
        screen.blit(player.image, (player_screen_x, player_screen_y))

        # Dibujar las posiciones de otros jugadores
        for other_id, other_data in client.other_players.items():
            if other_id == str(client.client_socket.getsockname()[1]):  # Omitir al jugador actual
                continue

            other_screen_x = int(other_data["x"] - player.x + config.SCREEN_WIDTH // 2 - player.width // 2)
            other_screen_y = int(other_data["y"] - player.y + config.SCREEN_HEIGHT // 2 - player.height // 2)
            pygame.draw.rect(screen, (0, 0, 255), (other_screen_x, other_screen_y, player.width, player.height))

        # Dibujar las balas activas
        player.draw_bullets(screen, player.x - config.SCREEN_WIDTH // 2, player.y - config.SCREEN_HEIGHT // 2)

        # Dibujar la salud del jugador
        health_surface = font.render(f"Salud: {player.health}", True, (255, 255, 255))
        screen.blit(health_surface, (10, 10))

        # Dibujar el arma equipada
        if player.current_weapon:
            weapon_surface = font.render(f"Arma: {player.current_weapon.name}", True, (255, 255, 255))
            screen.blit(weapon_surface, (10, 40))

        # Verificar si la salud llegó a cero
        if player.health <= 0:
            running = False
            game_over_surface = font.render("¡Game Over!", True, (255, 0, 0))
            screen.blit(game_over_surface, (config.SCREEN_WIDTH // 2 - 50, config.SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
