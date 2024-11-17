import socket
import threading
import json

class GameServer:
    def __init__(self, host="192.168.1.5", port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Diccionario para almacenar clientes y sus posiciones
        self.lock = threading.Lock()

    def handle_client(self, client_socket, client_address):
        client_id = client_address[1]
        print(f"Cliente conectado: {client_id}")

        # Inicializar la posición del cliente
        with self.lock:
            self.clients[client_id] = {"x": 0, "y": 0}

        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Decodificar el mensaje
                message = json.loads(data.decode())

                # Si es una actualización de posición
                if message["type"] == "position":
                    with self.lock:
                        self.clients[client_id]["x"] = message["x"]
                        self.clients[client_id]["y"] = message["y"]

                # Enviar actualizaciones a todos los clientes
                self.broadcast_positions()
        except (ConnectionResetError, json.JSONDecodeError):
            print(f"Cliente desconectado: {client_id}")
        finally:
            with self.lock:
                if client_id in self.clients:
                    del self.clients[client_id]
            client_socket.close()

    def broadcast_positions(self):
        with self.lock:
            positions = json.dumps({"type": "positions", "data": self.clients})
            for client_socket in self.clients.values():
                try:
                    client_socket.sendall(positions.encode())
                except:
                    pass

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Servidor iniciado en {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            thread.start()

if __name__ == "__main__":
    server = GameServer()
    server.start()
