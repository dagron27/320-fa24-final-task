import sys
import json
from server.server_logic import ServerGameLogic

class GameServer:
    def __init__(self):
        self.game_logic = ServerGameLogic()

    def process_command(self, command):
        action = command.get("action")
        if action == "move_left":
            self.game_logic.player.move("left")
        elif action == "move_right":
            self.game_logic.player.move("right")
        elif action == "shoot":
            missile = self.game_logic.player.shoot()
            self.game_logic.missiles.append(missile)
        elif action == "reset_game":
            self.game_logic.reset_game()
        self.game_logic.update_game_state()

    def get_game_state(self):
        return self.game_logic.get_game_state()

if __name__ == "__main__":
    server = GameServer()
    command = json.loads(sys.argv[1])
    server.process_command(command)
    print(json.dumps(server.get_game_state()))
