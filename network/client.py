# client.py

import socket
import pickle
import threading

# Configuración del cliente
SERVER_HOST = "192.168.1.5"  # Cambia esto a la IP del servidor
SERVER_PORT = 5555

# Estructura para almacenar datos compartidos
class ClientData:
    def __init__(self):
        self.player_id = None
        self.connected_player_ids = []
        self.received_data = []
        self.data_lock = threading.Lock()
        self.running = True  # Aseguramos que el atributo 'running' esté definido

client_data = ClientData()

# Crear socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(5.0)  # Tiempo de espera de 5 segundos

try:
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Conectado al servidor en {SERVER_HOST}:{SERVER_PORT}")
except Exception as e:
    print(f"Error al conectar al servidor: {e}")
    exit()

def send_message(message):
    if not client_data.running:
        return
    try:
        serialized_message = pickle.dumps(message)
        message_length = len(serialized_message)
        client_socket.sendall(message_length.to_bytes(4, 'big') + serialized_message)
    except Exception as e:
        print(f"Error al enviar datos al servidor: {e}")
        client_data.running = False
        client_socket.close()

def receive_messages():
    while client_data.running:
        try:
            # Leer la longitud del mensaje (primeros 4 bytes)
            data_length_bytes = client_socket.recv(4)
            if not data_length_bytes:
                print("Conexión cerrada por el servidor.")
                client_data.running = False
                break
            data_length = int.from_bytes(data_length_bytes, 'big')
            # Ahora leer los datos
            data = b''
            while len(data) < data_length:
                packet = client_socket.recv(data_length - len(data))
                if not packet:
                    print("Conexión cerrada por el servidor.")
                    client_data.running = False
                    break
                data += packet
            # Deserializar el mensaje
            message = pickle.loads(data)
            if "player_id" in message:
                client_data.player_id = message["player_id"]
            else:
                with client_data.data_lock:
                    client_data.received_data.append(message)
        except socket.timeout:
            continue  # Intentar recibir nuevamente
        except Exception as e:
            print(f"Error al recibir datos del servidor: {e}")
            client_data.running = False
            client_socket.close()
            break

# Iniciar el hilo para recibir datos
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

# Esperar a recibir el player_id
print("Esperando al servidor para recibir player_id...")
while client_data.player_id is None:
    pass  # Esperar hasta recibir el player_id

print(f"Conectado como jugador {client_data.player_id}")
