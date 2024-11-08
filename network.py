import socket
import threading
import pickle

class Network:
    def __init__(self, server_ip, port):
        # Inicializar el socket y conectar al servidor
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.port = port
        self.address = (self.server_ip, self.port)
        self.connect()  # Intentar conectar al servidor

    def connect(self):
        try:
            self.client.connect(self.address)
            print("Connected to the server.")
        except Exception as e:
            print("Could not connect to server:", e)

    def send(self, data):
        # Enviar datos al servidor
        try:
            self.client.sendall(pickle.dumps(data))
        except Exception as e:
            print("Error sending data:", e)

    def receive(self):
        # Recibir datos del servidor
        try:
            return pickle.loads(self.client.recv(4096))
        except Exception as e:
            print("Error receiving data:", e)
            return None

class Chat:
    def __init__(self, network):
        self.network = network
        self.chat_log = []  # Almacena mensajes de chat

    def send_message(self, message, recipient=None):
        # Enviar mensaje de chat al servidor
        data = {"type": "chat", "message": message, "recipient": recipient}
        self.network.send(data)

    def receive_messages(self):
        # Escucha los mensajes recibidos y actualiza el chat log
        while True:
            data = self.network.receive()
            if data and data.get("type") == "chat":
                self.chat_log.append(data["message"])
                print("Chat message:", data["message"])
