import socket
import threading

# Configuración básica
HOST = '192.168.1.5'  # Dirección del servidor
PORT = 65432        # Puerto de conexión

def receive_messages(sock):
    """
    Recibe mensajes del servidor y los imprime.
    """
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            print(f"{message}")
        except:
            print("[ERROR] Conexión perdida con el servidor.")
            sock.close()
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("[CONECTADO] Conectado al servidor.")

    # Iniciar hilo para recibir mensajes
    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        message = input("> ")
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    main()
