import socket
import threading
import pickle

class Server:
    def __init__(self, ip="0.0.0.0", port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen()
        print("Server started, waiting for connections...")
        
        self.clients = []  # Lista de conexiones de clientes
        
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            client, address = self.server.accept()
            print(f"New connection from {address}")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        while True:
            try:
                data = pickle.loads(client.recv(4096))
                if data:
                    print(f"Received data: {data}")
                    if data["type"] == "chat":
                        self.broadcast(data, client)
            except Exception as e:
                print("Error receiving data:", e)
                self.clients.remove(client)
                client.close()
                break

    def broadcast(self, data, sender_conn):
        for client in self.clients:
            if client != sender_conn:
                try:
                    client.sendall(pickle.dumps(data))
                except Exception as e:
                    print("Error sending data:", e)
                    self.clients.remove(client)

if __name__ == "__main__":
    server = Server(ip="0.0.0.0", port=5555)
