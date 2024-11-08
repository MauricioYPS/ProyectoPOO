# network/client.py

import socket
import threading

class GameClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position = (0, 0)  # Posición inicial del jugador
        self.other_player_position = (0, 0)  # Posición del otro jugador

    def connect_to_server(self):
        """Conecta al cliente al servidor."""
        try:
            self.client_socket.connect((self.host, self.port))
            print("Conectado al servidor")
            threading.Thread(target=self.receive_data).start()
        except ConnectionRefusedError:
            print("No se pudo conectar al servidor.")

    def send_position(self, position):
        """Envía la posición del jugador al servidor."""
        try:
            data = f"POS,{position[0]},{position[1]}"
            self.client_socket.sendall(data.encode())
        except BrokenPipeError:
            print("Conexión perdida con el servidor.")

    def receive_data(self):
        """Recibe datos del servidor."""
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                self.process_data(data)
            except ConnectionResetError:
                break
        self.client_socket.close()

    def process_data(self, data):
        """Procesa los datos recibidos del servidor."""
        data_parts = data.split(',')
        if data_parts[0] == "POS":
            # Actualiza la posición del otro jugador
            self.other_player_position = (int(data_parts[1]), int(data_parts[2]))

    def get_other_player_position(self):
        """Devuelve la posición del otro jugador."""
        return self.other_player_position

if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()
