import socket
import threading

# Configuración del servidor
HOST = "192.168.1.5"
PORT = 65432

# Diccionario para rastrear clientes y sus identificadores
clients = {}
client_counter = 1

# Función para manejar cada cliente
def handle_client(conn, addr):
    global client_counter
    client_id = f"Cliente {client_counter}"
    client_counter += 1

    print(f"[NUEVA CONEXIÓN] {client_id} conectado desde {addr}")
    clients[conn] = client_id

    try:
        while True:
            msg = conn.recv(1024).decode("utf-8")
            if not msg:
                break
            print(f"[{client_id}] {msg}")
            broadcast(f"[{client_id}] {msg}", conn)
    except ConnectionResetError:
        print(f"[DESCONECTADO] {client_id} se desconectó abruptamente.")
    finally:
        conn.close()
        del clients[conn]
        print(f"[DESCONECTADO] {client_id} desconectado.")

# Función para enviar mensajes a todos los clientes
def broadcast(msg, sender_conn):
    for client_conn in clients.keys():
        if client_conn != sender_conn:
            client_conn.send(msg.encode("utf-8"))

# Iniciar el servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[ESCUCHANDO] Servidor en {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[CONEXIONES ACTIVAS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("[INICIANDO] Servidor en inicio...")
    start_server()
