from game import Game

# Configuración del servidor (IP y puerto)
SERVER_IP = "192.168.1.8"  # Reemplaza con la IP de tu servidor si estás probando en red
PORT = 5555  # Puerto de conexión

def main():
    # Inicializar el juego
    game = Game(SERVER_IP, PORT)
    game.run()  # Ejecuta el bucle principal del juego

if __name__ == "__main__":
    main()
