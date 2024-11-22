import tkinter as tk
from game.game_logic import ClientGameLogic
from game.canvas_gui import GameCanvas
from game.game_state_updater import GameStateUpdater

class GameApp(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("River Raid")
        self.geometry("1000x1000")

        self.client = client
        self.game_logic = ClientGameLogic(client)

        # Create canvas and GUI elements
        self.canvas = GameCanvas(self, self.game_logic)
        self.info_label = tk.Label(self, text="Score: 0 | Lives: 3 | Fuel: 100")
        self.info_label.pack()

        self.bind("<Left>", lambda event: self.player_move("left"))
        self.bind("<Right>", lambda event: self.player_move("right"))
        self.bind("<space>", lambda event: self.player_shoot())
        self.bind("<Return>", lambda event: self.restart_game() if not self.game_logic.game_running else None)
        self.bind("<q>", lambda event: self.quit_game())

        self.tick_rate = 10

        # Start game state updater thread
        self.state_updater = GameStateUpdater(self.game_logic, self.client)
        self.state_updater.start()

        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        self._game_loop_running = False
        self.game_loop()

    def player_move(self, direction):
        if self.game_logic.game_running:
            self.game_logic.player.move(direction)
            self.canvas.update_canvas()

            self.client.send_message({"action": "move", "direction": direction})
            response = self.client.receive_message()
            if response.get('status') == 'ok':
                self.game_logic.update_game_state(response['game_state'])

    def player_shoot(self):
        if self.game_logic.game_running:
            self.game_logic.missiles.append(self.game_logic.player.shoot())
            self.canvas.update_canvas()

            self.client.send_message({"action": "shoot"})
            response = self.client.receive_message()
            if response.get('status') == 'ok':
                self.game_logic.update_game_state(response['game_state'])

    def game_loop(self):
        # Always process game states
        while not self.state_updater.update_queue.empty():
            game_state = self.state_updater.update_queue.get()
            self.game_logic.update_game_state(game_state)
        
        # Always update info label, regardless of game state
        self.info_label.config(text=f"Score: {self.game_logic.score} | Lives: {self.game_logic.lives} | Fuel: {self.game_logic.fuel}", font=("Helvetica", 25))

        if not self.game_logic.game_running:
            self.canvas.display_game_over()
        else:
            self.canvas.update_canvas()

        # Always schedule next iteration
        self.after(self.tick_rate, self.game_loop)

    def restart_game(self):
        self.client.send_message({"action": "reset_game"})
        response = self.client.receive_message()
        if response.get('status') == 'ok' and 'game_state' in response:
            print("Game Reset")
            self.game_logic.update_game_state(response['game_state'])
            self.info_label.config(text="Score: 0 | Lives: 3 | Fuel: 100")
            self.canvas.update_canvas()
        else:
            print("Failed to reset game: invalid response or missing game_state.")

    def quit_game(self):
        # Stop the game state updater thread
        self.state_updater.stop()
        self.client.send_message({"action": "quit_game"})
        self.client.close()  # Close the SSH connection
        self.quit()