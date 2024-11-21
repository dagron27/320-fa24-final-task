from network.network import ClientNetwork
from game.game_app import GameApp

if __name__ == "__main__":
    client = ClientNetwork()
    client.connect()

    # Initialize the game app and pass the client instance to it
    app = GameApp(client)
    app.mainloop()

    # Close the client connection when done
    client.close()
