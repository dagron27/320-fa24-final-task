from network.network import ClientNetwork
from game.game_manager import GameApp

if __name__ == "__main__":
    client = ClientNetwork()
    client.connect()

    app = GameApp(client)
    app.mainloop()

    client.close()
