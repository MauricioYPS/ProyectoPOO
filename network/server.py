# server.py

import socket
import threading
import pickle
import time
import math
import random
import os
import sys

import pygame  
from map.level1 import level_map
from entities.enemy import PatrollingEnemy, RandomEnemy, AggressiveEnemy, StationaryEnemy  # Importar clases de enemigos

# Configuración del servidor
HOST = '0.0.0.0'  # Dirección IP del servidor
PORT = 5555       # Puerto de conexión

# Variables globales
clients = {}  # Diccionario para almacenar clientes conectados {player_id: socket}
player_positions = {}  # Diccionario para almacenar posiciones de jugadores {player_id: {'x': x, 'y': y}}
player_id_counter = 0

enemies = {}  # Diccionario para almacenar enemigos {enemy_id: Enemy}
enemy_id_counter = 0
items = {}     # Diccionario para almacenar ítems en el mundo {item_id: ItemData}
item_id_counter = 0
TILE_SIZE = 40  # Tamaño de cada tile en píxeles

ATTACK_RANGE = 40  # Rango máximo de ataque en píxeles

# Definir la cantidad total de enemigos que deseas en el mapa
TOTAL_ENEMIES = 100  # Ajusta este número según tus necesidades

# Generar la lista de rectángulos de paredes
wall_rects = []
def build_wall_rects():
    for y, row in enumerate(level_map):
        for x, tile in enumerate(row):
            if tile == 1:  # Pared
                wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                wall_rects.append(wall_rect)
build_wall_rects()

# Clase ItemData para almacenar información de los ítems
class ItemData:
    def __init__(self, item_id, name, item_type, effect, x, y, image_path=None):
        self.item_id = item_id
        self.name = name
        self.type = item_type
        self.effect = effect
        self.x = x
        self.y = y
        self.is_broken = False
        self.image_path = image_path

def send_to_player(player_id, data):
    if player_id in clients:
        try:
            serialized_data = pickle.dumps(data)
            data_length = len(serialized_data)
            message_with_length = data_length.to_bytes(4, 'big') + serialized_data
            clients[player_id].sendall(message_with_length)
        except Exception as e:
            print(f"Error al enviar mensaje al jugador {player_id}: {e}")
            remove_player(player_id)

def broadcast(message, exclude_id=None):
    """
    Envía un mensaje a todos los clientes conectados, excepto al especificado.
    """
    serialized_data = pickle.dumps(message)
    data_length = len(serialized_data)
    message_with_length = data_length.to_bytes(4, 'big') + serialized_data
    for pid, client_socket in list(clients.items()):
        if pid == exclude_id:
            continue
        try:
            client_socket.sendall(message_with_length)
        except Exception as e:
            print(f"Error al enviar mensaje al jugador {pid}: {e}")
            remove_player(pid)

def remove_player(player_id):
    """
    Elimina un jugador de las listas de clientes y posiciones.
    """
    if player_id in clients:
        try:
            clients[player_id].close()
        except:
            pass
        del clients[player_id]
    if player_id in player_positions:
        del player_positions[player_id]
    # Enviar el evento 'remove_player' a todos los clientes
    broadcast({'remove_player': {'player_id': player_id}})
    # Actualizar la lista de IDs de jugadores
    broadcast({'player_ids': list(clients.keys())})
    print(f"Jugador {player_id} ha sido removido.")

def initialize_enemies():
    global enemies, enemy_id_counter

    # Definir los tipos de enemigos y su proporción
    enemy_types = [PatrollingEnemy, RandomEnemy, AggressiveEnemy, StationaryEnemy]
    enemy_type_weights = [0.25, 0.25, 0.25, 0.25]  # Distribución equitativa

    generated_enemies = 0
    max_attempts = TOTAL_ENEMIES * 10  # Para evitar bucles infinitos
    attempts = 0

    while generated_enemies < TOTAL_ENEMIES and attempts < max_attempts:
        attempts += 1
        # Seleccionar aleatoriamente el tipo de enemigo basado en las proporciones
        enemy_class = random.choices(enemy_types, weights=enemy_type_weights, k=1)[0]

        # Generar una posición aleatoria dentro del mapa
        x_tile = random.randint(0, len(level_map[0]) - 1)
        y_tile = random.randint(0, len(level_map) - 1)
        x = x_tile * TILE_SIZE
        y = y_tile * TILE_SIZE

        enemy_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        # Verificar si la posición está libre (no es una pared y no hay otro enemigo)
        collision = False
        for wall in wall_rects:
            if wall.colliderect(enemy_rect):
                collision = True
                break
        if collision:
            continue
        for enemy in enemies.values():
            if enemy.rect.colliderect(enemy_rect):
                collision = True
                break
        if collision:
            continue

        # Crear una instancia del enemigo
        if enemy_class == PatrollingEnemy:
            # Definir puntos de patrulla para el enemigo
            patrol_points = [
                (x, y),
                (x + TILE_SIZE * random.randint(3, 7), y),
                (x + TILE_SIZE * random.randint(3, 7), y + TILE_SIZE * random.randint(3, 7)),
                (x, y + TILE_SIZE * random.randint(3, 7))
            ]
            enemy = PatrollingEnemy(x, y, patrol_points)
        elif enemy_class == RandomEnemy:
            enemy = RandomEnemy(x, y)
        elif enemy_class == AggressiveEnemy:
            enemy = AggressiveEnemy(x, y)
        elif enemy_class == StationaryEnemy:
            enemy = StationaryEnemy(x, y)
        else:
            continue  # Tipo de enemigo no reconocido

        # Asignar un ID único al enemigo
        enemy.enemy_id = enemy_id_counter
        enemies[enemy_id_counter] = enemy
        enemy_id_counter += 1
        generated_enemies += 1

    print(f"Inicializados {generated_enemies} enemigos en el mapa.")

def generate_random_weapon():
    weapons = [
        {"name": "sword", "image_path": "assets/sword.png", "type": "weapon", "effect": 10},
        {"name": "potion", "image_path": "assets/potion.png", "type": "potion", "effect": 20},
    ]
    return random.choice(weapons)

def initialize_items():
    global item_id_counter, items
    for y, row in enumerate(level_map):
        for x, tile in enumerate(row):
            if tile == 2:
                barrel = ItemData(
                    item_id_counter,
                    'Barril',
                    'barrel',
                    0,
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    image_path="assets/barrel.png"
                )
                items[item_id_counter] = barrel
                item_id_counter += 1
            elif tile == 3:
                potion = ItemData(
                    item_id_counter,
                    'Poción de Salud',
                    'potion',
                    50,
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    image_path="assets/potion.png"
                )
                items[item_id_counter] = potion
                item_id_counter += 1

def handle_client(conn, addr, player_id):
    global player_positions, item_id_counter, items
    try:
        # Enviar el player_id al cliente
        serialized_data = pickle.dumps({'player_id': player_id})
        data_length = len(serialized_data)
        conn.sendall(data_length.to_bytes(4, 'big') + serialized_data)
        print(f"Jugador {player_id} conectado desde {addr}.")

        while True:
            # Recibir el tamaño del mensaje (4 bytes)
            data_length_bytes = conn.recv(4)
            if not data_length_bytes:
                print(f"No se recibieron datos del jugador {player_id}.")
                break
            data_length = int.from_bytes(data_length_bytes, 'big')
            # Recibir el mensaje completo
            data = b''
            while len(data) < data_length:
                packet = conn.recv(data_length - len(data))
                if not packet:
                    break
                data += packet
            if not data:
                print(f"No se recibieron datos del jugador {player_id}.")
                break
            try:
                message = pickle.loads(data)

                if 'position' in message:
                    player_positions[player_id] = message['position']

                elif 'pickup' in message:
                    item_id = message['pickup']['item_id']
                    if item_id in items:
                        del items[item_id]
                        broadcast({'remove_item': {'item_id': item_id}})
                        print(f"Jugador {player_id} recogió el ítem {item_id}.")

                elif 'type' in message:
                    if message['type'] == 'global':
                        chat_content = message.get('chat', '')
                        formatted_message = f"[Global] Jugador {player_id}: {chat_content}"
                        broadcast({'chat': formatted_message}, exclude_id=player_id)
                        print(f"Jugador {player_id} envió mensaje global: {chat_content}")

                    elif message['type'] == 'private':
                        recipient_id = message.get('recipient_id')
                        chat_content = message.get('chat', '')
                        if recipient_id in clients:
                            formatted_message_recipient = f"[Privado] Jugador {player_id}: {chat_content}"
                            send_to_player(recipient_id, {'chat': formatted_message_recipient})
                            print(f"Jugador {player_id} envió mensaje privado a {recipient_id}: {chat_content}")
                        else:
                            formatted_message = f"[Error] Jugador {recipient_id} no está conectado."
                            send_to_player(player_id, {'chat': formatted_message})
                            print(f"Jugador {player_id} intentó enviar mensaje privado a {recipient_id}, pero no está conectado.")

                    elif message['type'] == 'attack':
                        enemy_id = message.get('enemy_id')
                        if enemy_id in enemies:
                            enemy = enemies[enemy_id]
                            if enemy.health > 0:
                                attacker_pos = player_positions.get(player_id, {'x': 0, 'y': 0})
                                attacker_x = attacker_pos['x']
                                attacker_y = attacker_pos['y']
                                enemy_x = enemy.rect.x
                                enemy_y = enemy.rect.y
                                distance = math.hypot(attacker_x - enemy_x, attacker_y - enemy_y)
                                if distance <= ATTACK_RANGE:
                                    attack_damage = 25
                                    enemy.health -= attack_damage
                                    print(f"Jugador {player_id} atacó al Enemigo {enemy_id}. Salud restante: {enemy.health}")
                                    if enemy.health <= 0:
                                        del enemies[enemy_id]
                                        broadcast({'remove_enemy': {'enemy_id': enemy_id}})
                                        print(f"Enemigo {enemy_id} ha sido derrotado por el Jugador {player_id}.")
                                else:
                                    formatted_message = f"[Error] Enemigo {enemy_id} está fuera de rango."
                                    send_to_player(player_id, {'chat': formatted_message})
                                    print(f"Jugador {player_id} intentó atacar al Enemigo {enemy_id}, pero está fuera de rango.")
                        else:
                            formatted_message = f"[Error] Enemigo {enemy_id} no existe."
                            send_to_player(player_id, {'chat': formatted_message})
                            print(f"Jugador {player_id} intentó atacar al Enemigo {enemy_id}, pero no existe.")

                    elif message['type'] == 'equip':
                        weapon_name = message.get('weapon_name')
                        if weapon_name:
                            equip_info = {
                                'player_id': player_id,
                                'weapon_name': weapon_name
                            }
                            broadcast({'other_equip': equip_info}, exclude_id=player_id)
                            print(f"Jugador {player_id} equipó {weapon_name}.")

                    elif message['type'] == 'break_barrel':
                        item_id = message.get('item_id')
                        if item_id in items:
                            item = items[item_id]
                            if item.type == 'barrel' and not item.is_broken:
                                item.is_broken = True
                                weapon = generate_random_weapon()
                                weapon_item = ItemData(
                                    item_id=item_id_counter,
                                    name=weapon['name'],
                                    item_type=weapon['type'],
                                    effect=weapon['effect'],
                                    x=item.x,
                                    y=item.y,
                                    image_path=weapon['image_path']
                                )
                                items[item_id_counter] = weapon_item
                                barrel_broken_message = {
                                    'barrel_broken': {
                                        'barrel_id': item_id,
                                        'weapon': {
                                            'name': weapon_item.name,
                                            'type': weapon_item.type,
                                            'effect': weapon_item.effect,
                                            'x': weapon_item.x,
                                            'y': weapon_item.y,
                                            'item_id': weapon_item.item_id,
                                            'image_path': weapon_item.image_path
                                        }
                                    }
                                }
                                broadcast(barrel_broken_message)
                                print(f"Jugador {player_id} rompió el barril {item_id} y generó el ítem {weapon_item.name}.")
                                item_id_counter += 1

                    elif message['type'] == 'death':
                        print(f"Jugador {player_id} ha muerto.")
                        break  # Salir del bucle para desconectar al jugador

                    else:
                        pass

            except Exception as e:
                print(f"Error al procesar el mensaje del jugador {player_id}: {e}")
                break

    except Exception as e:
        print(f"Error con la conexión del jugador {player_id}: {e}")
    finally:
        remove_player(player_id)
        conn.close()

def send_damage_to_player(player_id, damage):
    """
    Envía un mensaje de daño al jugador especificado.
    """
    message = {
        'damage': {
            'target_id': player_id,
            'type': 'player',
            'amount': damage
        }
    }
    send_to_player(player_id, message)

def update_enemies():
    while True:
        for enemy in list(enemies.values()):
            enemy.update(player_positions, send_damage_to_player, walls=wall_rects)
        time.sleep(0.016)  # Aproximadamente 60 FPS

def broadcast_loop():
    while True:
        data = {
            'positions': player_positions,
            'player_ids': list(clients.keys()),
            'enemies': {enemy_id: {
                'x': enemy.rect.x,
                'y': enemy.rect.y,
                'health': enemy.health,
                'enemy_id': enemy.enemy_id,
                'type': enemy.__class__.__name__
            } for enemy_id, enemy in enemies.items()},
            'items': {item_id: {
                'name': item.name,
                'type': item.type,
                'effect': item.effect,
                'x': item.x,
                'y': item.y,
                'item_id': item.item_id,
                'is_broken': item.is_broken if item.type == 'barrel' else False,
                'image_path': item.image_path
            } for item_id, item in items.items()}
        }
        try:
            serialized_data = pickle.dumps(data)
            data_length = len(serialized_data)
            message_with_length = data_length.to_bytes(4, 'big') + serialized_data
            for pid, client_socket in list(clients.items()):
                try:
                    client_socket.sendall(message_with_length)
                except Exception as e:
                    print(f"Error al enviar estado del juego al jugador {pid}: {e}")
                    remove_player(pid)
        except Exception as e:
            print(f"Error al serializar los datos del juego: {e}")
        time.sleep(0.05)  # Enviar actualizaciones cada 50 ms

def start_server():
    global player_id_counter
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
    except Exception as e:
        print(f"No se pudo enlazar el servidor en {HOST}:{PORT}: {e}")
        sys.exit()
    server_socket.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}")

    # Iniciar hilos para actualizar enemigos y broadcast
    threading.Thread(target=update_enemies, daemon=True).start()
    threading.Thread(target=broadcast_loop, daemon=True).start()

    while True:
        try:
            conn, addr = server_socket.accept()
            player_id = player_id_counter
            clients[player_id] = conn
            player_positions[player_id] = {'x': TILE_SIZE * 5, 'y': TILE_SIZE * 5}  # Posición inicial
            player_id_counter += 1
            threading.Thread(target=handle_client, args=(conn, addr, player_id), daemon=True).start()
        except Exception as e:
            print(f"Error al aceptar una nueva conexión: {e}")

if __name__ == "__main__":
    pygame.init()
    initialize_enemies()
    initialize_items()
    start_server()
