from game import Game

SERVER_IP = "192.168.1.5"
PORT = 5555

def main():
    game = Game(SERVER_IP, PORT)
    game.run()

if __name__ == "__main__":
    main()
