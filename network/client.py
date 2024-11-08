# network/client.py

import socket
import threading
import time

class GameClient:
    def __init__(self, host='192.168.1.5', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position = (0.0, 0.0)  # Posición inicial del jugador como flotante
        self.other_player_position = (0.0, 0.0)  # Posición del otro jugador como flotante
        self.chat_messages = []  # Lista de mensajes de chat [(mensaje, tiempo)]
        self.player_id = None  # ID del jugador asignado por el servidor
        self.other_player_id = None  # ID del otro jugador
        self.received_events = []  # Lista de eventos recibidos del otro jugador

    def connect_to_server(self):
        """Conecta al cliente al servidor."""
        try:
            self.client_socket.connect((self.host, self.port))
            print("Conectado al servidor")
            threading.Thread(target=self.receive_data, daemon=True).start()
        except ConnectionRefusedError:
            print("No se pudo conectar al servidor.")

    def send_position(self, position):
        """Envía la posición del jugador al servidor."""
        try:
            data = f"POS,{position[0]},{position[1]}\n"  # Añadir un delimitador al final
            self.client_socket.sendall(data.encode())
        except (BrokenPipeError, OSError):
            print("Error: No se pudo enviar la posición. Conexión cerrada.")

    def send_chat_message(self, message, recipient):
        """Envía un mensaje de chat al servidor."""
        try:
            data = f"CHAT,{recipient},{message}\n"
            self.client_socket.sendall(data.encode())
        except (BrokenPipeError, OSError):
            print("Error: No se pudo enviar el mensaje de chat. Conexión cerrada.")

    def receive_data(self):
        """Recibe datos del servidor."""
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("Conexión cerrada por el servidor.")
                    break
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    self.process_data(message)
            except (ConnectionResetError, OSError):
                print("Error: Conexión perdida con el servidor.")
                break
        self.client_socket.close()

    def process_data(self, data):
        """Procesa los datos recibidos del servidor."""
        data_parts = data.split(',')
        if data_parts[0] == "POS":
            # Datos de posición de otro jugador
            try:
                sender_id = int(data_parts[1])
                x = float(data_parts[2])
                y = float(data_parts[3])

                if sender_id != self.player_id:
                    self.other_player_position = (x, y)
                    self.other_player_id = sender_id
                    # Registrar el evento de movimiento del otro jugador
                    self.received_events.append({
                        'type': 'movement',
                        'time': time.time(),
                        'player_id': sender_id,
                        'data': {'position': (x, y)}
                    })
            except ValueError:
                print(f"Error al convertir los datos recibidos: {data}")
        elif data_parts[0] == "CHAT":
            # Mensaje de chat recibido
            sender_id = int(data_parts[1])
            recipient = data_parts[2]
            chat_message = ",".join(data_parts[3:])
            if recipient == 'Global' or recipient == f'Jugador {self.player_id}':
                # Almacenar el mensaje de chat con la marca de tiempo actual
                self.chat_messages.append((f"Jugador {sender_id}: {chat_message}", time.time()))
                print(f"Mensaje recibido: {chat_message}")
                # Registrar el evento de chat del otro jugador
                if sender_id != self.player_id:
                    self.received_events.append({
                        'type': 'chat',
                        'time': time.time(),
                        'player_id': sender_id,
                        'data': {
                            'recipient': recipient,
                            'message': chat_message
                        }
                    })
        elif data_parts[0] == "ID":
            # Asignar el ID del jugador
            self.player_id = int(data_parts[1])
            print(f"ID asignado por el servidor: {self.player_id}")

    def get_chat_messages(self):
        """Devuelve los mensajes de chat visibles dentro de los últimos 7 segundos."""
        current_time = time.time()
        # Filtrar mensajes dentro del límite de tiempo y limpiar mensajes antiguos
        self.chat_messages = [(msg, msg_time) for msg, msg_time in self.chat_messages if current_time - msg_time <= 7]
        return [msg for msg, _ in self.chat_messages]

    def get_other_player_position(self):
        """Devuelve la posición del otro jugador."""
        return self.other_player_position

    def get_other_player_id(self):
        """Devuelve el ID del otro jugador."""
        return self.other_player_id

    def get_received_events(self):
        """Devuelve los eventos recibidos del otro jugador."""
        return self.received_events.copy()

    def clear_received_events(self):
        """Limpia los eventos recibidos."""
        self.received_events.clear()

if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()
