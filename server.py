import socket
import threading
import pickle
import uuid

class Server:
    def __init__(self, ip="0.0.0.0", port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen()
        print("Server started. Waiting for connections...")  # Mensaje al iniciar el servidor

        self.clients = []  # Lista de conexiones de clientes

    def handle_client(self, conn, addr):
        print(f"New connection: {addr}")
        self.clients.append(conn)
        
        while True:
            try:
                data = pickle.loads(conn.recv(4096))
                if data and data.get("type") == "chat":
                    data["id"] = str(uuid.uuid4())  # Asigna un ID único al mensaje
                    self.broadcast(data, conn)
            except Exception as e:
                print("Error handling client:", e)
                self.clients.remove(conn)
                conn.close()
                break

# En el archivo server.py, en la clase Server
    def broadcast(self, data, sender_conn):
        for client in self.clients:
            if client != sender_conn:  # Excluir al cliente que envió el mensaje originalmente
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
