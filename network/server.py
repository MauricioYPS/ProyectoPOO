# network/server.py

import socket
import threading

class GameServer:
    def __init__(self, host='192.168.1.5', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}  # Diccionario para almacenar conexiones {ID: conn}
        self.next_player_id = 1  # ID para asignar a los jugadores

    def start_server(self):
        """Inicia el servidor y escucha conexiones entrantes."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)  # Permitimos hasta 2 conexiones (2 jugadores)
        print("Servidor iniciado, esperando conexiones...")

        while True:
            conn, addr = self.server_socket.accept()
            player_id = self.next_player_id
            self.next_player_id += 1
            self.connections[player_id] = conn
            print(f"Conexión establecida con {addr}, asignado ID {player_id}")
            threading.Thread(target=self.handle_client, args=(conn, player_id)).start()

    def handle_client(self, conn, player_id):
        """Maneja los mensajes recibidos de cada jugador."""
        try:
            # Enviar el ID al jugador
            conn.sendall(f"ID,{player_id}\n".encode())

            while True:
                data = conn.recv(1024)
                if not data:
                    print("Sin datos recibidos. Cerrando conexión.")
                    break
                self.process_data(data, conn, player_id)
        except ConnectionResetError:
            print("Error: El cliente cerró la conexión de forma inesperada.")
        finally:
            conn.close()
            del self.connections[player_id]
            print(f"Conexión con jugador {player_id} cerrada.")

    def process_data(self, data, sender_conn, sender_id):
        """Procesa y enruta los datos recibidos."""
        messages = data.decode().split('\n')
        for message in messages:
            if not message:
                continue
            data_parts = message.split(',')
            if data_parts[0] == "POS":
                # Añadir el ID del remitente al mensaje antes de reenviarlo
                new_message = f"POS,{sender_id},{data_parts[1]},{data_parts[2]}\n"
                self.broadcast(new_message.encode(), sender_conn)
            elif data_parts[0] == "CHAT":
                recipient = data_parts[1]
                chat_message = ','.join(data_parts[2:])
                self.route_chat_message(sender_id, recipient, chat_message)

    def broadcast(self, data, sender_conn):
        """Envía datos a todos los jugadores excepto al remitente."""
        for conn in self.connections.values():
            if conn != sender_conn:
                try:
                    conn.sendall(data)
                except BrokenPipeError:
                    print("Error: No se pudo enviar datos al cliente.")

    def route_chat_message(self, sender_id, recipient, message):
        """Enruta el mensaje de chat al destinatario correspondiente."""
        data = f"CHAT,{sender_id},{recipient},{message}\n".encode()
        if recipient == 'Global':
            # Enviar a todos menos al remitente
            for conn in self.connections.values():
                try:
                    conn.sendall(data)
                except BrokenPipeError:
                    print("Error: No se pudo enviar mensaje al cliente.")
        else:
            # Enviar al destinatario específico
            recipient_id = None
            if recipient == 'Jugador 1':
                recipient_id = 1
            elif recipient == 'Jugador 2':
                recipient_id = 2

            if recipient_id and recipient_id in self.connections:
                conn = self.connections[recipient_id]
                try:
                    conn.sendall(data)
                except BrokenPipeError:
                    print("Error: No se pudo enviar mensaje al cliente.")
            else:
                print(f"Destinatario {recipient} no encontrado.")

if __name__ == "__main__":
    server = GameServer()
    server.start_server()
