from network.network import ClientNetwork
from game.game_logic import GameLogic

if __name__ == "__main__":
    client = ClientNetwork()
    client.connect()

    # Initialize the game logic
    game = GameLogic(client)

    # Start and run the game
    game.start_game()

    # Close the client connection when done
    client.close()
