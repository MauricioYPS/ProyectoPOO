# network/client.py

import socket
import threading

class GameClient:
    def __init__(self, host='192.168.1.5', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.position = (0.0, 0.0)  # Posición inicial del jugador como flotante
        self.other_player_position = (0.0, 0.0)  # Posición del otro jugador como flotante

    def connect_to_server(self):
        """Conecta al cliente al servidor."""
        try:
            self.client_socket.connect((self.host, self.port))
            print("Conectado al servidor")
            # Iniciar un hilo para recibir datos sin bloquear Pygame
            threading.Thread(target=self.receive_data, daemon=True).start()
        except ConnectionRefusedError:
            print("No se pudo conectar al servidor.")

    def send_position(self, position):
        """Envía la posición del jugador al servidor."""
        try:
            data = f"POS,{position[0]},{position[1]}"
            self.client_socket.sendall(data.encode())
        except (BrokenPipeError, OSError):
            print("Error: No se pudo enviar la posición. Conexión cerrada.")

    def receive_data(self):
        """Recibe datos del servidor."""
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("Conexión cerrada por el servidor.")
                    break
                self.process_data(data)
            except (ConnectionResetError, OSError):
                print("Error: Conexión perdida con el servidor.")
                break
        self.client_socket.close()

    def process_data(self, data):
        """Procesa los datos recibidos del servidor."""
        data_parts = data.split(',')
        if data_parts[0] == "POS":
            # Actualiza la posición del otro jugador usando valores flotantes
            try:
                self.other_player_position = (float(data_parts[1]), float(data_parts[2]))
            except ValueError:
                print(f"Error al convertir los datos recibidos: {data}")

    def get_other_player_position(self):
        """Devuelve la posición del otro jugador."""
        return self.other_player_position

if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()
