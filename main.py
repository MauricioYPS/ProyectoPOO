# main.py

import pygame
from entities.player import Player
from entities.entity import Entity
from entities.item import Item
from entities.barrel import Barrel
from entities.inventory import Inventory
from entities.enemy import PatrollingEnemy, RandomEnemy, AggressiveEnemy, StationaryEnemy  # Importar clases de enemigos
from network.client import send_message, client_data
from map.level1 import level_map
import threading
import time
import math
import os
import sys
import json

# Inicialización de Pygame y Pygame Mixer
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
TILE_SIZE = 40  # Tamaño de cada tile en píxeles
MAP_WIDTH = len(level_map[0]) * TILE_SIZE
MAP_HEIGHT = len(level_map) * TILE_SIZE

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laberinto en el casitllo")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)

# Reloj para controlar la tasa de frames
clock = pygame.time.Clock()

# Fuentes para el texto
font = pygame.font.Font(None, 24)
font_private = pygame.font.Font(None, 24)

chat_log = []  # Almacena los mensajes del chat
input_text = ""  # Texto que el jugador escribe
chat_open = False  # Indica si el campo de chat está abierto
chat_mode = "global"  # Modo de chat por defecto
selected_recipient = None  # ID del jugador seleccionado para mensajes privados
show_menu = False  # Indica si el menú de selección está abierto
menu_options = []  # Opciones del menú
selected_option_index = 0  # Índice de la opción seleccionada

# Control de envío de posiciones
send_position_interval = 0.05  # Enviar cada 50 ms (20 veces por segundo)
last_position_send_time = 0

# Control de cooldown de ataque del jugador
player_attack_cooldown = 0
player_attack_cooldown_time = 0.5  # 0.5 segundos entre ataques

# Definición del rango de ataque
ATTACK_RANGE = 40  # Debe coincidir con la definición en el servidor

# Modo Replay
replay_mode = False
replay_events = []
replay_start_time = 0
replay_index = 0

# Flag para manejar el cierre del juego
game_over_flag = False

# Función callback para manejar la muerte del jugador
def on_player_death():
    global game_over_flag
    game_over_flag = True
    # Enviar mensaje de muerte al servidor
    send_message({'type': 'death'})
    print("Has muerto. Desconectando del servidor...")
    # Reproducir sonido de muerte antes de cerrar
    death_sound.play()
    pygame.time.delay(1000)  # Esperar 1 segundo para que se reproduzca el sonido
    pygame.quit()
    sys.exit()

# Esperar a recibir player_id antes de continuar (solo en modo normal)
if not (len(sys.argv) > 1 and sys.argv[1] == '--replay'):
    print("Esperando al servidor para recibir player_id...")
    while client_data.player_id is None:
        time.sleep(0.1)
    print(f"Conectado como jugador {client_data.player_id}")

# Crear jugador local (solo en modo normal)
if not (len(sys.argv) > 1 and sys.argv[1] == '--replay'):
    start_x = TILE_SIZE * 5  # Columna 5
    start_y = TILE_SIZE * 5  # Fila 5
    player = Player(start_x, start_y, on_death_callback=on_player_death)
else:
    player = None  # No se necesita un jugador en modo replay

# Otros jugadores
other_players = {}

# Enemigos
enemies = {}

# Cambiar world_items a un diccionario
world_items = {}

# Cargar imágenes para los tiles
def load_tile_image(path, fallback_color):
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image
    except pygame.error as e:
        print(f"Error al cargar la imagen {path}: {e}")
        fallback_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        fallback_image.fill(fallback_color)
        return fallback_image

# Asegúrate de tener las imágenes en la carpeta 'assets'
wall_image = load_tile_image('assets/wall.png', (139, 69, 19))  # Marrón para las paredes
floor_image = load_tile_image('assets/floor.png', (222, 184, 135))  # Arena para el suelo

# Lista para las rects de las paredes (para colisiones)
wall_rects = []

# Construir el mapa y almacenar las rects de las paredes y barriles
def build_map():
    for y, row in enumerate(level_map):
        for x, tile in enumerate(row):
            if tile == 1:
                wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                wall_rects.append(wall_rect)
            elif tile == 2:
                # Crear un barril en esta posición
                barrel = Barrel(x * TILE_SIZE, y * TILE_SIZE)
                world_items[len(world_items)] = barrel  # Asigna un ID único al barril
            elif tile == 3:
                # Crear un ítem (por ejemplo, una poción)
                potion = Item(
                    name="Poción de Salud",
                    image_path="assets/potion.png",
                    item_type="potion",
                    effect=50
                )
                potion.rect.x = x * TILE_SIZE
                potion.rect.y = y * TILE_SIZE
                potion.item_id = len(world_items)
                world_items[potion.item_id] = potion

build_map()

# Clase para otros jugadores
class OtherPlayer:
    def __init__(self, player_id, x, y):
        self.player_id = player_id
        self.rect = pygame.Rect(x, y, 40, 40)
        self.base_image = pygame.Surface((40, 40))
        self.base_image.fill((0, 255, 0))
        self.image = pygame.image.load('assets/prota.png').convert_alpha()
        self.prev_pos = pygame.math.Vector2(x, y)
        self.target_pos = pygame.math.Vector2(x, y)
        self.last_update_time = time.time()
        self.interp_time = 0.1  # Tiempo de interpolación en segundos
        self.weapon = None  # Arma equipada

    def update_position(self, x, y):
        self.prev_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.target_pos = pygame.math.Vector2(x, y)
        self.last_update_time = time.time()

    def update(self):
        # Interpolar entre prev_pos y target_pos
        now = time.time()
        t = (now - self.last_update_time) / self.interp_time
        t = min(t, 1.0)
        new_pos = self.prev_pos.lerp(self.target_pos, t)
        self.rect.x = new_pos.x
        self.rect.y = new_pos.y

    def update_image(self):
        self.image = self.base_image.copy()
        if self.weapon:
            try:
                self.image = pygame.image.load('assets/prota.png').convert_alpha()
                weapon_image = pygame.image.load(self.weapon.image_path).convert_alpha()
                weapon_image = pygame.transform.scale(weapon_image, (30, 30))  # Escalar para ajustar
                self.image.blit(weapon_image, (5, 5))  # Ajustar posición según sea necesario
            except pygame.error as e:
                print(f"Error al cargar la imagen del arma {self.weapon.name}: {e}")

# Desplazamiento del mapa (cámara)
camera_x, camera_y = 0, 0

# Función para agregar mensajes al chat_log con colores
def add_chat_message(message, message_type="global"):
    if message_type == "global":
        chat_log.append({
            "message": message,
            "timestamp": time.time(),
            "color": BLUE  # Color para mensajes globales
        })
    elif message_type == "private_sent":
        chat_log.append({
            "message": message,
            "timestamp": time.time(),
            "color": ORANGE  # Color para mensajes privados enviados
        })
    elif message_type == "private_received":
        chat_log.append({
            "message": message,
            "timestamp": time.time(),
            "color": GREEN  # Color para mensajes privados recibidos
        })
    elif message_type == "error":
        chat_log.append({
            "message": message,
            "timestamp": time.time(),
            "color": RED  # Color para errores
        })
    else:
        chat_log.append({
            "message": message,
            "timestamp": time.time(),
            "color": BLACK  # Color por defecto
        })

# Función para cargar eventos de replay
def load_replay(log_file):
    global replay_events, replay_start_time
    try:
        with open(log_file, 'r') as f:
            replay_events = json.load(f)
        replay_events.sort(key=lambda event: event['time'])  # Asegurarse de que están ordenados
        replay_start_time = time.time()
        print(f"Reproduciendo replay desde {log_file}")
    except Exception as e:
        print(f"Error al cargar el archivo de replay: {e}")
        sys.exit(1)

# Clase para manejar la reproducción de eventos
class ReplayManager:
    def __init__(self, events):
        self.events = events
        self.start_time = time.time()
        self.current_event = 0
        self.total_events = len(events)

    def update(self):
        current_time = time.time() - self.start_time
        while self.current_event < self.total_events and self.events[self.current_event]['time'] <= current_time:
            event = self.events[self.current_event]
            process_replay_event(event)
            self.current_event += 1

    def is_finished(self):
        return self.current_event >= self.total_events

def process_replay_event(event):
    global player, other_players, enemies, world_items, chat_log
    message = event.get('message', {})
    event_type = event.get('type', '')

    if event_type == 'broadcast' or event_type == 'broadcast_loop':
        # Procesar el estado completo del juego
        data = message
        # Actualizar posiciones de jugadores
        positions = data.get('positions', {})
        for pid, pos in positions.items():
            if pid == client_data.player_id:
                if player:
                    player.rect.x = pos['x']
                    player.rect.y = pos['y']
            else:
                if pid not in other_players:
                    other_players[pid] = OtherPlayer(pid, pos['x'], pos['y'])
                else:
                    other_players[pid].update_position(pos['x'], pos['y'])

        # Actualizar IDs de jugadores conectados
        client_data.connected_player_ids = data.get('player_ids', [])

        # Actualizar enemigos
        enemies_data = data.get('enemies', {})
        enemies.clear()
        for enemy_id, enemy_info in enemies_data.items():
            if enemy_info['type'] == 'PatrollingEnemy':
                enemy = PatrollingEnemy(enemy_info['x'], enemy_info['y'], [])
            elif enemy_info['type'] == 'RandomEnemy':
                enemy = RandomEnemy(enemy_info['x'], enemy_info['y'])
            elif enemy_info['type'] == 'AggressiveEnemy':
                enemy = AggressiveEnemy(enemy_info['x'], enemy_info['y'])
            elif enemy_info['type'] == 'StationaryEnemy':
                enemy = StationaryEnemy(enemy_info['x'], enemy_info['y'])
            else:
                enemy = Entity(enemy_info['x'], enemy_info['y'], 40, 40)
            enemy.health = enemy_info['health']
            enemy.enemy_id = enemy_info['enemy_id']
            enemies[enemy_id] = enemy

        # Actualizar ítems
        items_data = data.get('items', {})
        world_items.clear()
        for item_id, item_info in items_data.items():
            if item_info['type'] == 'weapon':
                item = Item(
                    name=item_info['name'],
                    image_path=item_info['image_path'],
                    item_type=item_info['type'],
                    effect=item_info['effect']
                )
            elif item_info['type'] == 'barrel':
                item = Barrel(item_info['x'], item_info['y'])
                item.is_broken = item_info.get('is_broken', False)
            elif item_info['type'] == 'potion':
                item = Item(
                    name=item_info['name'],
                    image_path=item_info['image_path'],
                    item_type=item_info['type'],
                    effect=item_info['effect']
                )
            else:
                item = Item(
                    name=item_info['name'],
                    image_path=item_info['image_path'],
                    item_type=item_info['type'],
                    effect=item_info['effect']
                )
            item.rect.x = item_info['x']
            item.rect.y = item_info['y']
            item.item_id = item_info['item_id']
            world_items[item_id] = item

    elif event_type == 'send_to_player':
        # Procesar mensajes específicos enviados a este cliente
        if 'chat' in message:
            chat_message = message['chat']
            if "[Privado]" in chat_message:
                add_chat_message(chat_message, "private_received")
            elif "[Error]" in chat_message:
                add_chat_message(chat_message, "error")
            else:
                add_chat_message(chat_message, "global")
        elif 'damage' in message:
            damage_info = message['damage']
            target_id = damage_info.get('target_id')
            damage_type = damage_info.get('type')  # 'enemy' o 'player'
            amount = damage_info.get('amount')
            
            if damage_type == 'enemy' and target_id in enemies:
                enemies[target_id].health -= amount
                damage_enemy_sound.play()  # Reproducir sonido de daño al enemigo
                if enemies[target_id].health <= 0:
                    del enemies[target_id]
                    # Puedes agregar efectos visuales de muerte del enemigo aquí
            elif damage_type == 'player' and target_id == client_data.player_id:
                if player:
                    player.receive_damage(amount)
                    damage_player_sound.play()  # Reproducir sonido de daño al jugador
                    print(f"Has recibido {amount} de daño. Salud restante: {player.health}")
                    if player.health <= 0:
                        print("¡Has sido derrotado!")
                        death_sound.play()  # Reproducir sonido de muerte
                        on_player_death()  # Manejar la muerte del jugador
        elif 'other_equip' in message:
            equip_info = message['other_equip']
            pid = equip_info['player_id']
            weapon_name = equip_info['weapon_name']
            if pid in other_players:
                other_player = other_players[pid]
                # Crear un ítem temporal para representar el arma equipada
                weapon = Item(
                    name=weapon_name,
                    image_path=f"assets/{weapon_name.lower()}.png",
                    item_type='weapon',
                    effect=25
                )
                other_player.weapon = weapon
                other_player.update_image()
    elif event_type == 'remove_player':
        pid = event['player_id']
        if pid in other_players:
            del other_players[pid]
            print(f"Jugador {pid} ha sido removido del juego.")
    elif event_type == 'player_connected':
        # En el replay, no conectamos nuevos jugadores
        pass
    else:
        pass

# Cargar sonidos
pygame.mixer.music.load('assets/sounds/background_music.mp3')
pygame.mixer.music.set_volume(0.5)  # Ajusta el volumen entre 0.0 y 1.0
pygame.mixer.music.play(-1)  # Reproducir en bucle infinito

attack_sound = pygame.mixer.Sound('assets/sounds/attack.mp3')
damage_enemy_sound = pygame.mixer.Sound('assets/sounds/damage_enemy.mp3')
damage_player_sound = pygame.mixer.Sound('assets/sounds/damage_player.mp3')
death_sound = pygame.mixer.Sound('assets/sounds/death.mp3')

# Opcional: Ajustar volúmenes
attack_sound.set_volume(0.7)
damage_enemy_sound.set_volume(0.6)
damage_player_sound.set_volume(0.6)
death_sound.set_volume(1.0)

# Loop principal
running = True
replay_manager = None

if len(sys.argv) > 1 and sys.argv[1] == '--replay':
    if len(sys.argv) > 2:
        replay_file = sys.argv[2]
        load_replay(replay_file)
        replay_manager = ReplayManager(replay_events)
        replay_mode = True
    else:
        print("Por favor, proporciona el archivo de replay. Uso: python main.py --replay replay_log.json")
        sys.exit(1)

while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if chat_open:
                if show_menu:
                    # Manejo del menú de selección
                    if event.key == pygame.K_UP:
                        # Mover selección hacia arriba
                        selected_option_index = (selected_option_index - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        # Mover selección hacia abajo
                        selected_option_index = (selected_option_index + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        # Seleccionar la opción actual
                        selected_option = menu_options[selected_option_index]
                        if selected_option == "Global":
                            chat_mode = "global"
                            selected_recipient = None
                        else:
                            # Enviar mensaje privado al jugador seleccionado
                            try:
                                recipient_id = int(selected_option.split(" ")[1])  # Asumimos formato "Jugador X"
                                chat_mode = "private"
                                selected_recipient = recipient_id
                            except (IndexError, ValueError):
                                chat_mode = "global"
                                selected_recipient = None
                        show_menu = False
                    elif event.key == pygame.K_ESCAPE:
                        # Cerrar el menú sin seleccionar
                        show_menu = False
                else:
                    if event.key == pygame.K_RETURN:  # Enviar mensaje con Enter
                        if input_text:
                            if chat_mode == "global":
                                send_message({
                                    "type": "global",
                                    "chat": input_text
                                })
                                # Mostrar el mensaje en el chat_log
                                add_chat_message(f"[Global] Tú: {input_text}", "global")
                            elif chat_mode == "private" and selected_recipient is not None:
                                send_message({
                                    "type": "private",
                                    "recipient_id": selected_recipient,
                                    "chat": input_text
                                })
                                # Mostrar el mensaje en el chat_log
                                add_chat_message(f"[Privado a Jugador {selected_recipient}] Tú: {input_text}", "private_sent")
                            input_text = ""
                    elif event.key == pygame.K_ESCAPE:
                        chat_open = False  # Cerrar chat con Escape
                    elif event.key == pygame.K_BACKSPACE:  # Borrar texto
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_TAB:
                        # Abrir menú de selección
                        show_menu = True
                        # Acceder a connected_player_ids de manera segura
                        if not replay_mode:
                            if client_data.connected_player_ids:
                                menu_options = ["Global"] + [f"Jugador {pid}" for pid in client_data.connected_player_ids if pid != client_data.player_id]
                            else:
                                menu_options = ["Global"]
                        else:
                            menu_options = ["Global"]  # En replay, no hay otros jugadores
                        selected_option_index = 0  # Resetear la selección al abrir el menú
                    else:  # Agregar carácter
                        input_text += event.unicode
            else:
                if event.key == pygame.K_t:
                    chat_open = True  # Abrir chat al presionar 'T'
                    chat_mode = "global"
                    selected_recipient = None
                elif event.key in [pygame.K_1, pygame.K_2]:
                    # Usar ítems del inventario
                    index = event.key - pygame.K_1
                    if not replay_mode and player and len(player.inventory.items) > index:
                        item = player.inventory.items[index]
                        player.inventory.use_item(item, player)
                        if item.type == 'weapon':
                            # Enviar mensaje de equipamiento al servidor
                            send_message({
                                "type": "equip",
                                "weapon_name": item.name
                            })
                            # Opcional: Mostrar mensaje en el chat local
                            add_chat_message(f"[Equipado] Has equipado: {item.name}", "global")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not replay_mode:
                if event.button == 1:  # Clic izquierdo del ratón
                    if player_attack_cooldown <= 0:
                        # Identificar el enemigo o barril más cercano al jugador
                        closest_enemy_id = None
                        closest_barrel_id = None
                        closest_enemy_distance = float('inf')
                        closest_barrel_distance = float('inf')
                        if player:
                            player_center = player.rect.center

                            # Buscar enemigos en rango
                            for enemy_id, enemy in enemies.items():
                                enemy_center = enemy.rect.center
                                dx = enemy_center[0] - player_center[0]
                                dy = enemy_center[1] - player_center[1]
                                distance = math.hypot(dx, dy)
                                if distance < closest_enemy_distance:
                                    closest_enemy_distance = distance
                                    closest_enemy_id = enemy_id

                            # Buscar barriles en rango
                            for item_id, item in world_items.items():
                                if isinstance(item, Barrel):
                                    barrel_center = item.rect.center
                                    dx = barrel_center[0] - player_center[0]
                                    dy = barrel_center[1] - player_center[1]
                                    distance = math.hypot(dx, dy)
                                    if distance < closest_barrel_distance:
                                        closest_barrel_distance = distance
                                        closest_barrel_id = item_id

                            # Priorizar atacar enemigos si están en rango
                            if closest_enemy_id is not None and closest_enemy_distance <= ATTACK_RANGE:
                                # Enviar mensaje de ataque al servidor
                                send_message({
                                    "type": "attack",
                                    "enemy_id": closest_enemy_id
                                })
                                player_attack_cooldown = player_attack_cooldown_time
                                attack_sound.play()  # Reproducir sonido de ataque
                            elif closest_barrel_id is not None and closest_barrel_distance <= ATTACK_RANGE:
                                # Enviar mensaje para romper el barril al servidor
                                send_message({
                                    "type": "break_barrel",
                                    "item_id": closest_barrel_id
                                })
                                player_attack_cooldown = player_attack_cooldown_time
                                attack_sound.play()  # Reproducir sonido de ataque
                            else:
                                # Opcional: Mostrar mensaje de que no hay objetivos en rango
                                add_chat_message(f"[Info] No hay objetivos en rango para atacar.", "global")

    # Control de cooldown de ataque del jugador
    if not replay_mode:
        if player_attack_cooldown > 0:
            player_attack_cooldown -= clock.get_time() / 1000.0  # Convertir ms a segundos
            if player_attack_cooldown < 0:
                player_attack_cooldown = 0

    # Controles del jugador local (solo si el chat no está abierto y no está en modo replay)
    if not chat_open and not replay_mode and not game_over_flag:
        keys = pygame.key.get_pressed()
        if player:
            player.move(keys, wall_rects)

    # Enviar posición del jugador local al servidor a intervalos (solo en modo normal)
    if not replay_mode and not game_over_flag:
        current_time_send = time.time()
        if current_time_send - last_position_send_time > send_position_interval:
            if player:
                send_message({"position": {"x": player.rect.x, "y": player.rect.y}})
            last_position_send_time = current_time_send

    # Procesar datos recibidos (solo en modo normal)
    if not replay_mode and not game_over_flag:
        with client_data.data_lock:
            while client_data.received_data:
                message = client_data.received_data.pop(0)
                if "positions" in message:
                    positions = message["positions"]
                    for pid, pos in positions.items():
                        if pid == client_data.player_id:
                            continue
                        if pid not in other_players:
                            # Crear nuevo OtherPlayer
                            other_players[pid] = OtherPlayer(pid, pos["x"], pos["y"])
                        else:
                            # Actualizar posición
                            other_players[pid].update_position(pos["x"], pos["y"])
                if "player_ids" in message:
                    client_data.connected_player_ids = message["player_ids"]
                if "enemies" in message:
                    enemies_data = message["enemies"]
                    # Actualizar enemigos locales
                    for enemy_id, enemy_info in enemies_data.items():
                        if enemy_id not in enemies:
                            # Crear nuevo enemigo
                            enemy_type = enemy_info.get('type', 'Enemy')
                            if enemy_type == 'PatrollingEnemy':
                                enemy = PatrollingEnemy(enemy_info['x'], enemy_info['y'], [])
                                enemy.image = pygame.image.load('assets/enemy1.png').convert_alpha()
                            elif enemy_type == 'RandomEnemy':
                                enemy = RandomEnemy(enemy_info['x'], enemy_info['y'])
                                enemy.image = pygame.image.load('assets/enemy2.png').convert_alpha()
                            elif enemy_type == 'AggressiveEnemy':
                                enemy = AggressiveEnemy(enemy_info['x'], enemy_info['y'])
                                enemy.image = pygame.image.load('assets/enemy3.png').convert_alpha()
                            elif enemy_type == 'StationaryEnemy':
                                enemy = StationaryEnemy(enemy_info['x'], enemy_info['y'])
                                enemy.image = pygame.image.load('assets/enemy4.png').convert_alpha()
                            else:
                                enemy = Entity(enemy_info['x'], enemy_info['y'], 40, 40)
                                enemy.image.fill(BLACK)
                            enemy.health = enemy_info['health']
                            enemy.enemy_id = enemy_info['enemy_id']
                            enemies[enemy_id] = enemy
                        else:
                            # Actualizar posición y salud
                            enemy = enemies[enemy_id]
                            enemy.rect.x = enemy_info['x']
                            enemy.rect.y = enemy_info['y']
                            enemy.health = enemy_info['health']
                    # Eliminar enemigos que ya no existen
                    enemy_ids = set(enemies.keys())
                    server_enemy_ids = set(enemies_data.keys())
                    for enemy_id in enemy_ids - server_enemy_ids:
                        del enemies[enemy_id]
                if "items" in message:
                    items_data = message["items"]
                    # Actualizar ítems locales
                    for item_id, item_info in items_data.items():
                        if item_id not in world_items:
                            # Crear nuevo ítem
                            if item_info.get('type') == 'weapon':
                                item = Item(
                                    item_info['name'],
                                    item_info.get('image_path'),  # Usamos get para evitar KeyError
                                    item_info['type'],
                                    effect=item_info['effect']
                                )
                            elif item_info.get('type') == 'barrel':
                                # Crear un barril
                                item = Barrel(item_info['x'], item_info['y'])
                                item.is_broken = item_info.get('is_broken', False)
                            elif item_info.get('type') == 'potion':
                                item = Item(
                                    item_info['name'],
                                    item_info.get('image_path'),
                                    item_info['type'],
                                    effect=item_info['effect']
                                )
                            else:
                                item = Item(
                                    item_info['name'],
                                    item_info.get('image_path'),  # Usamos get para evitar KeyError
                                    item_info['type'],
                                    effect=item_info['effect']
                                )
                            item.rect.x = item_info['x']
                            item.rect.y = item_info['y']
                            item.item_id = item_info['item_id']
                            world_items[item_id] = item
                        else:
                            # Actualizar el estado del ítem si es un barril
                            if item_info.get('type') == 'barrel':
                                barrel = world_items[item_id]
                                if isinstance(barrel, Barrel):
                                    barrel.is_broken = item_info.get('is_broken', False)
                if 'remove_item' in message:
                    item_id = message['remove_item']['item_id']
                    if item_id in world_items:
                        del world_items[item_id]
                if 'remove_enemy' in message:
                    enemy_id = message['remove_enemy']['enemy_id']
                    if enemy_id in enemies:
                        del enemies[enemy_id]
                if 'damage' in message:
                    damage_info = message['damage']
                    target_id = damage_info.get('target_id')
                    damage_type = damage_info.get('type')  # 'enemy' o 'player'
                    amount = damage_info.get('amount')
                    
                    if damage_type == 'enemy' and target_id in enemies:
                        enemies[target_id].health -= amount
                        damage_enemy_sound.play()  # Reproducir sonido de daño al enemigo
                        if enemies[target_id].health <= 0:
                            del enemies[target_id]
                    elif damage_type == 'player' and target_id == client_data.player_id:
                        if player:
                            player.receive_damage(amount)
                            damage_player_sound.play()  # Reproducir sonido de daño al jugador
                            print(f"Has recibido {amount} de daño. Salud restante: {player.health}")
                            if player.health <= 0:
                                print("¡Has sido derrotado!")
                                death_sound.play()  # Reproducir sonido de muerte
                                on_player_death()  # Manejar la muerte del jugador
                if 'other_equip' in message:
                    equip_info = message['other_equip']
                    pid = equip_info['player_id']
                    weapon_name = equip_info['weapon_name']
                    if pid in other_players:
                        other_player = other_players[pid]
                        # Crear un ítem temporal para representar el arma equipada
                        weapon = Item(
                            weapon_name,
                            f"assets/{weapon_name.lower()}.png",
                            'weapon',
                            effect=25
                        )
                        other_player.weapon = weapon
                        other_player.update_image()
                if "chat" in message:
                    # Determinar si el mensaje es privado recibido, global o error
                    chat_message = message["chat"]
                    if "[Privado]" in chat_message:
                        add_chat_message(chat_message, "private_received")
                        print(f"Mensaje privado recibido: {chat_message}")
                    elif "[Error]" in chat_message:
                        add_chat_message(chat_message, "error")  # Mostrar errores en rojo
                        print(f"Error recibido: {chat_message}")
                    else:
                        add_chat_message(chat_message, "global")
                        print(f"Mensaje global recibido: {chat_message}")

                # Manejar mensajes de barriles rotos y armas generadas
                if "barrel_broken" in message:
                    barrel_id = message["barrel_broken"]["barrel_id"]
                    weapon_info = message["barrel_broken"]["weapon"]
                    if barrel_id in world_items:
                        barrel = world_items[barrel_id]
                        if isinstance(barrel, Barrel) and not barrel.is_broken:
                            barrel.is_broken = True
                            # Generar el arma y agregarla al mundo
                            weapon = Item(
                                name=weapon_info["name"],
                                image_path=weapon_info.get("image_path"),  # Usamos get para evitar KeyError
                                item_type=weapon_info["type"],
                                effect=weapon_info["effect"]
                            )
                            weapon.rect.x = barrel.rect.x
                            weapon.rect.y = barrel.rect.y
                            weapon.item_id = weapon_info["item_id"]
                            world_items[weapon.item_id] = weapon

                if "spawn_weapon" in message:
                    weapon_info = message["spawn_weapon"]
                    weapon = Item(
                        name=weapon_info["name"],
                        image_path=weapon_info.get("image_path"),  # Usamos get para evitar KeyError
                        item_type=weapon_info["type"],
                        effect=weapon_info["effect"]
                    )
                    weapon.rect.x = weapon_info["x"]
                    weapon.rect.y = weapon_info["y"]
                    weapon.item_id = weapon_info["item_id"]
                    world_items[weapon.item_id] = weapon

                # Manejar el evento 'remove_player' en modo normal
                if 'remove_player' in message:
                    pid = message['remove_player']['player_id']
                    if pid in other_players:
                        del other_players[pid]
                        print(f"Jugador {pid} ha sido removido del juego.")

    # En modo replay, actualizar los eventos de replay
    if replay_mode and replay_manager:
        replay_manager.update()
        if replay_manager.is_finished():
            print("Replay completada.")
            running = False

    # Eliminar mensajes que tienen más de 6 segundos (solo en modo normal)
    if not replay_mode and not game_over_flag:
        chat_log = [msg for msg in chat_log if current_time - msg["timestamp"] <= 6]

    if not replay_mode and not game_over_flag:
        # Actualizar posición de la cámara
        if player:
            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2

            # Limitar la cámara a los límites del mapa
            camera_x = max(0, min(camera_x, MAP_WIDTH - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, MAP_HEIGHT - SCREEN_HEIGHT))
    elif not game_over_flag:
        # En modo replay, centrar la cámara en una posición fija
        camera_x = 0
        camera_y = 0

    # Dibujar el mapa
    for y, row in enumerate(level_map):
        for x, tile in enumerate(row):
            tile_x = x * TILE_SIZE - camera_x
            tile_y = y * TILE_SIZE - camera_y

            # Comprobar si la tile está dentro de la pantalla
            if tile_x < -TILE_SIZE or tile_x > SCREEN_WIDTH or tile_y < -TILE_SIZE or tile_y > SCREEN_HEIGHT:
                continue  # No dibujar tiles fuera de la pantalla

            # Dibujar siempre el suelo
            screen.blit(floor_image, (tile_x, tile_y))

            # Dibujar paredes encima del suelo
            if tile == 1:
                screen.blit(wall_image, (tile_x, tile_y))

    # Dibujar ítems (incluyendo barriles) en el mundo
    for item in world_items.values():
        if isinstance(item, Barrel):
            item.draw(screen, camera_x, camera_y)
        else:
            try:
                item_image = pygame.image.load(item.image_path).convert_alpha()
                item_image = pygame.transform.scale(item_image, (TILE_SIZE, TILE_SIZE))
                screen.blit(item_image, (item.rect.x - camera_x, item.rect.y - camera_y))
            except pygame.error as e:
                print(f"Error al cargar la imagen del ítem {item.name}: {e}")
                # Dibujar una superficie por defecto si falla la carga
                fallback_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_image.fill(GREEN)
                screen.blit(fallback_image, (item.rect.x - camera_x, item.rect.y - camera_y))

    # Comprobar si el jugador recoge un ítem (solo en modo normal)
    if not replay_mode and player and not game_over_flag:
        for item_id, item in list(world_items.items()):
            if player.rect.colliderect(item.rect):
                if not isinstance(item, Barrel):
                    # Recoger el ítem
                    player.inventory.add_item(item)
                    print(f"Has obtenido: {item.name}")
                    # Enviar mensaje al servidor para informar de la recogida
                    send_message({'pickup': {'item_id': item_id}})
                    # Reproducir sonido de recolección (opcional)
                    # collection_sound.play()
                    # Eliminar el ítem localmente
                    del world_items[item_id]

    # Dibujar enemigos
    for enemy in enemies.values():
        if hasattr(enemy, 'health') and enemy.health > 0:
            try:
                screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))
            except pygame.error as e:
                print(f"Error al dibujar el enemigo {enemy.enemy_id}: {e}")
                # Dibujar una superficie por defecto si falla la carga
                fallback_enemy = pygame.Surface((40, 40))
                fallback_enemy.fill(RED)
                screen.blit(fallback_enemy, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

    # Actualizar y dibujar otros jugadores
    for other_player in other_players.values():
        other_player.update()
        screen.blit(other_player.image, (other_player.rect.x - camera_x, other_player.rect.y - camera_y))

    # Dibujar jugador local (solo en modo normal)
    if not replay_mode and player and not game_over_flag:
        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

    # Mostrar el player_id y la salud en pantalla (solo en modo normal)
    if not replay_mode and player and not game_over_flag:
        pid_text = f"Tu ID: {client_data.player_id}"
        pid_surface = font.render(pid_text, True, BLACK)
        screen.blit(pid_surface, (10, 10))

        health_text = font.render(f"Salud: {player.health}/{player.max_health}", True, BLACK)
        screen.blit(health_text, (10, 40))

    # Mostrar el inventario en pantalla (solo en modo normal)
    if not replay_mode and player and not game_over_flag:
        inventory_text = font.render("Inventario:", True, BLACK)
        screen.blit(inventory_text, (10, 70))
        for idx, item in enumerate(player.inventory.items):
            item_text = font.render(f"{idx + 1}. {item.name}", True, BLACK)
            screen.blit(item_text, (10, 90 + idx * 20))

    # Dibujar chat
    chat_display_start = SCREEN_HEIGHT - 150
    chat_messages = chat_log[-5:]  # Mostrar los últimos 5 mensajes
    for i, msg in enumerate(chat_messages):
        text_surface = font.render(msg["message"], True, msg["color"])
        screen.blit(text_surface, (10, chat_display_start + i * 20))

    # Mostrar texto que el jugador está escribiendo (solo en modo normal)
    if chat_open and not replay_mode:
        # Mostrar el destinatario si es un mensaje privado
        if chat_mode == "private" and selected_recipient is not None:
            input_prompt = f"[Privado a Jugador {selected_recipient}]: > {input_text}"
        else:
            input_prompt = f"> {input_text}"
        input_surface = font.render(input_prompt, True, BLACK)
        screen.blit(input_surface, (10, SCREEN_HEIGHT - 30))
        if show_menu:
            # Dibujar menú de selección
            menu_x, menu_y = 10, SCREEN_HEIGHT - 200
            for idx, option in enumerate(menu_options):
                if idx == selected_option_index:
                    color = YELLOW  # Resaltar la opción seleccionada
                else:
                    color = BLACK
                menu_surface = font.render(option, True, color)
                screen.blit(menu_surface, (menu_x, menu_y + idx * 20))

    # Mostrar texto que el jugador está escribiendo (solo en modo replay)
    if chat_open and replay_mode:
        input_prompt = f"[Replay]: > {input_text}"
        input_surface = font.render(input_prompt, True, BLACK)
        screen.blit(input_surface, (10, SCREEN_HEIGHT - 30))
        if show_menu:
            # Dibujar menú de selección (no funcional en replay)
            menu_x, menu_y = 10, SCREEN_HEIGHT - 200
            for idx, option in enumerate(menu_options):
                if idx == selected_option_index:
                    color = YELLOW  # Resaltar la opción seleccionada
                else:
                    color = BLACK
                menu_surface = font.render(option, True, color)
                screen.blit(menu_surface, (menu_x, menu_y + idx * 20))

    # Actualizar pantalla
    pygame.display.flip()

    # Controlar la tasa de frames
    clock.tick(60)

    # Verificar si el jugador ha muerto para cerrar el juego
    if game_over_flag:
        print("Cerrando el juego por muerte del jugador...")
        running = False

    # En modo replay, actualizar los eventos de replay
    if replay_mode and replay_manager:
        replay_manager.update()
        if replay_manager.is_finished():
            print("Replay completada.")
            running = False

    # En modo normal, centrar la cámara en el jugador
    if not replay_mode and not game_over_flag:
        if player:
            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2

            # Limitar la cámara a los límites del mapa
            camera_x = max(0, min(camera_x, MAP_WIDTH - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, MAP_HEIGHT - SCREEN_HEIGHT))
    elif not game_over_flag:
        # En modo replay, centrar la cámara en una posición fija
        camera_x = 0
        camera_y = 0

# Finalizar Pygame
if replay_mode and replay_manager and replay_manager.is_finished():
    print("Finalizando replay.")

pygame.quit()
