import socket
import threading
import pickle

class Network:
    def __init__(self, server_ip, port):
        # Inicialización de red (socket)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.port = port
        self.address = (self.server_ip, self.port)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.address)
            print("Connected to the server.")
        except Exception as e:
            print("Could not connect to server:", e)

    def send(self, data):
        try:
            self.client.sendall(pickle.dumps(data))
        except Exception as e:
            print("Error sending data:", e)

    def receive(self):
        try:
            return pickle.loads(self.client.recv(4096))
        except Exception as e:
            print("Error receiving data:", e)
            return None

class Chat:
    def __init__(self, network):
        self.network = network
        self.chat_log = []  # Log de mensajes de chat
        
        # Lanzar el hilo para escuchar mensajes
        threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def send_message(self, message, recipient=None):
        data = {"type": "chat", "message": message, "recipient": recipient}
        self.network.send(data)

    def listen_for_messages(self):
        while True:
            data = self.network.receive()
            if data and data.get("type") == "chat":
                self.chat_log.append(data["message"])
                print("Chat message received:", data["message"])

