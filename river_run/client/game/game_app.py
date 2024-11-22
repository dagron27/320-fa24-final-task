import tkinter as tk
from game.game_logic import ClientGameLogic

class GameApp(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("River Raid")
        self.geometry("1000x1000")

        # Set canvas background color to gray
        self.canvas = tk.Canvas(self, width=1000, height=950, bg="gray")
        self.canvas.pack()
        
        self.info_label = tk.Label(self, text="Score: 0 | Lives: 3 | Fuel: 100")
        self.info_label.pack()

        self.bind("<Left>", lambda event: self.player_move("left"))
        self.bind("<Right>", lambda event: self.player_move("right"))
        self.bind("<space>", lambda event: self.player_shoot())
        self.bind("<Return>", lambda event: self.restart_game())
        self.bind("<q>", lambda event: self.quit_game())  # Change to quit_game to handle cleanup

        self.client = client
        self.game_logic = ClientGameLogic(client)
        self.tick_rate = 200

        # Bind the window close event to the quit_game function
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        self.game_loop()

    def player_move(self, direction):
        if self.game_logic.game_running:
            # Immediate feedback
            self.game_logic.player.move(direction)
            self.update_canvas()

            # Send move command to server
            self.client.send_message({"action": "move", "direction": direction})
            response = self.client.receive_message()
            if response.get('status') == 'ok':
                self.game_logic.update_game_state(response['game_state'])

    def player_shoot(self):
        if self.game_logic.game_running:
            # Immediate feedback
            self.game_logic.missiles.append(self.game_logic.player.shoot())
            self.update_canvas()

            # Send shoot command to server
            self.client.send_message({"action": "shoot"})
            response = self.client.receive_message()
            if response.get('status') == 'ok':
                self.game_logic.update_game_state(response['game_state'])

    def game_loop(self):
        if not self.game_logic.game_running:
            self.display_game_over()
            return

        # Regularly update the game state from the server
        self.client.send_message({"action": "get_game_state"})
        response = self.client.receive_message()
        print("Received game state response:", response)  # Add detailed logging
        if response.get('status') == 'ok':
            self.game_logic.update_game_state(response['game_state'])

        self.update_canvas()
        self.info_label.config(text=f"Score: {self.game_logic.score} | Lives: {self.game_logic.lives} | Fuel: {self.game_logic.fuel}", font=("Helvetica", 25))
        self.after(self.tick_rate, self.game_loop)  # Schedule the next game loop iteration

    def update_canvas(self):
        self.canvas.delete("all")

        if self.game_logic.game_running:
            self.canvas.create_rectangle(
                self.game_logic.player.x * 30,
                self.game_logic.player.y * 30,
                (self.game_logic.player.x + 1) * 30,
                (self.game_logic.player.y + 1) * 30,
                fill="blue"
            )

            for obs in self.game_logic.obstacles:
                self.canvas.create_rectangle(
                    obs.x * 30,
                    obs.y * 30,
                    (obs.x + 1) * 30,
                    (obs.y + 1) * 30,
                    fill="red"
                )

            for depot in self.game_logic.fuel_depots:
                self.canvas.create_rectangle(
                    depot.x * 30,
                    depot.y * 30,
                    (depot.x + 1) * 30,
                    (depot.y + 1) * 30,
                    fill="green"
                )

            for missile in self.game_logic.missiles:
                self.canvas.create_line(
                    missile.x * 30 + 15,
                    missile.y * 30,
                    missile.x * 30 + 15,
                    (missile.y + 1) * 30,
                    fill="yellow"
                )
        else:
            self.display_game_over()

    def display_game_over(self):
        self.canvas.delete("all")
        self.canvas.create_text((1000/2), (950/2), text="Game Over", fill="red", font=("Helvetica", 100))
        self.info_label.config(text=f"Final Score: {self.game_logic.score}")

    def restart_game(self):
        if not self.game_logic.game_running:
            self.game_logic.reset_game()
            self.info_label.config(text="Score: 0 | Lives: 3 | Fuel: 100")
            self.game_loop()

    def quit_game(self):
        self.client.send_message({"action": "stop_server"})  # Send stop signal to server
        self.quit()  # Quit the GUI application