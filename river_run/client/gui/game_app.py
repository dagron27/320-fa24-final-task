import tkinter as tk
from shared.entities import Player, Obstacle, FuelDepot, Missile
from client.client_logic import ClientGameLogic

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("River Raid")
        self.geometry("300x350")
        
        self.canvas = tk.Canvas(self, width=300, height=300, bg="gray")
        self.canvas.pack()
        
        self.info_label = tk.Label(self, text="Score: 0 | Lives: 3 | Fuel: 100")
        self.info_label.pack()

        self.bind("<Left>", lambda event: self.player_move("left"))
        self.bind("<Right>", lambda event: self.player_move("right"))
        self.bind("<space>", lambda event: self.player_shoot())
        self.bind("<Return>", lambda event: self.restart_game()) 
        self.bind("<q>", lambda event: self.quit())

        self.game_logic = ClientGameLogic()
        self.tick_rate = 200

        self.game_loop()

    def player_move(self, direction):
        if self.game_logic.game_running:
            self.game_logic.player_move(direction)
            self.update_canvas()

    def player_shoot(self):
        if self.game_logic.game_running:
            self.game_logic.player_shoot()
            self.update_canvas()

    def game_loop(self):
        if not self.game_logic.game_running:
            self.display_game_over()
            return

        self.game_logic.update_game_state()
        self.update_canvas()
        self.info_label.config(text=f"Score: {self.game_logic.score} | Lives: {self.game_logic.lives} | Fuel: {self.game_logic.fuel}")
        self.after(self.tick_rate, self.game_loop)

    def update_canvas(self):
        self.canvas.delete("all")

        if self.game_logic.game_running:
            self.canvas.create_rectangle(self.game_logic.player.x * 30, self.game_logic.player.y * 30,
                                         (self.game_logic.player.x + 1) * 30, (self.game_logic.player.y + 1) * 30, fill="blue")

            for obs in self.game_logic.obstacles:
                self.canvas.create_rectangle(obs.x * 30, obs.y * 30, (obs.x + 1) * 30, (obs.y + 1) * 30, fill="red")

            for depot in self.game_logic.fuel_depots:
                self.canvas.create_rectangle(depot.x * 30, depot.y * 30, (depot.x + 1) * 30, (depot.y + 1) * 30, fill="green")

            for missile in self.game_logic.missiles:
                self.canvas.create_line(missile.x * 30 + 15, missile.y * 30, missile.x * 30 + 15, (missile.y + 1) * 30, fill="yellow")
        else:
            self.display_game_over()

    def display_game_over(self):
        self.canvas.delete("all")
        self.canvas.create_text(150, 150, text="Game Over", fill="red", font=("Helvetica", 24))
        self.info_label.config(text=f"Final Score: {self.game_logic.score}")

    def restart_game(self):
        if not self.game_logic.game_running:
            self.game_logic.reset_game()
            self.info_label.config(text="Score: 0 | Lives: 3 | Fuel: 100")
            self.game_loop()
