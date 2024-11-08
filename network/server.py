# network/server.py

import socket
import threading

class GameServer:
    def __init__(self, host='192.168.1.5', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Almacena las conexiones de los jugadores

    def start_server(self):
        """Inicia el servidor y escucha conexiones entrantes."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)  # Permitimos hasta 2 conexiones (2 jugadores)
        print("Servidor iniciado, esperando conexiones...")

        while len(self.connections) < 2:
            conn, addr = self.server_socket.accept()
            print(f"Conexión establecida con {addr}")
            self.connections.append(conn)
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        """Maneja los mensajes recibidos de cada jugador."""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print("Sin datos recibidos. Cerrando conexión.")
                    break
                self.broadcast(data, conn)  # Reenvía datos a todos los demás jugadores
        except ConnectionResetError:
            print("Error: El cliente cerró la conexión de forma inesperada.")
        finally:
            conn.close()
            self.connections.remove(conn)
            print("Conexión cerrada.")

    def broadcast(self, data, sender_conn):
        """Envía datos a todos los jugadores excepto al remitente."""
        for conn in self.connections:
            if conn != sender_conn:
                try:
                    conn.sendall(data)
                except BrokenPipeError:
                    print("Error: No se pudo enviar datos al cliente.")

if __name__ == "__main__":
    server = GameServer()
    server.start_server()
