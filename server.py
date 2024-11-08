import socket
import threading
import pickle

class Server:
    def __init__(self, ip="0.0.0.0", port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen()
        print("Server started. Waiting for connections...")  # Mensaje al iniciar el servidor

        self.clients = []  # Lista de conexiones de clientes

    def handle_client(self, conn, addr):
        print(f"New connection from {addr}")  # Mensaje al recibir una nueva conexión
        self.clients.append(conn)
        
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                data = pickle.loads(data)
                print(f"Received data from {addr}: {data}")  # Mensaje para mostrar datos recibidos
                self.broadcast(data, conn)
        
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        
        finally:
            print(f"Client {addr} disconnected.")
            conn.close()
            self.clients.remove(conn)

    def broadcast(self, data, sender_conn):
        # Enviar datos a todos los clientes, excepto el remitente
        for client in self.clients:
            if client != sender_conn:
                try:
                    client.sendall(pickle.dumps(data))
                except Exception as e:
                    print("Error sending data:", e)

    def start(self):
        print("Server is running and listening for clients...")
        while True:
            conn, addr = self.server.accept()
            print(f"Accepted new connection from {addr}")  # Mensaje al aceptar una conexión
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    server = Server(ip="0.0.0.0", port=5555)
    server.start()
