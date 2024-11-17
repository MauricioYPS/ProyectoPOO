import socket
import threading
import json
class GameClient:
    def __init__(self, host="192.168.1.5", port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_players = {}  # Almacena posiciones de otros jugadores

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))
        thread = threading.Thread(target=self.listen_to_server, daemon=True)
        thread.start()

    def listen_to_server(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                # Decodificar el mensaje
                message = json.loads(data.decode())

                if message["type"] == "positions":
                    self.other_players = message["data"]
        except:
            print("Desconectado del servidor.")
        finally:
            self.client_socket.close()

    def send_position(self, x, y):
        try:
            message = json.dumps({"type": "position", "x": x, "y": y})
            self.client_socket.sendall(message.encode())
        except:
            print("Error al enviar la posición al servidor.")

if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()
