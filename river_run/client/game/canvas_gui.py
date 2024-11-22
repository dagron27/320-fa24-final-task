import tkinter as tk

class GameCanvas(tk.Canvas):
    def __init__(self, parent, game_logic):
        super().__init__(parent, width=1000, height=950, bg="gray")
        self.game_logic = game_logic
        self.pack()

    def update_canvas(self):
        self.delete("all")
        if self.game_logic.game_running:
            self.create_rectangle(
                self.game_logic.player.x * 30,
                self.game_logic.player.y * 30,
                (self.game_logic.player.x + 1) * 30,
                (self.game_logic.player.y + 1) * 30,
                fill="blue"
            )

            for depot in self.game_logic.fuel_depots:
                self.create_rectangle(
                    depot.x * 30,
                    depot.y * 30,
                    (depot.x + 1) * 30,
                    (depot.y + 1) * 30,
                    fill="green"
                )

            for missile in self.game_logic.missiles:
                self.create_line(
                    missile.x * 30 + 15,
                    missile.y * 30,
                    missile.x * 30 + 15,
                    (missile.y + 1) * 30,
                    fill="yellow"
                )

            # Add specific enemies with different sizes and colors 
            for enemy in self.game_logic.enemies: 
                color = "red" # Default color for enemy 
                width = 30 
                height = 30 
                
                if enemy.type == "B": 
                    color = "purple" # Boats 
                    width = 80 
                    height = 20 
                elif enemy.type == "J": 
                    color = "orange" # Jets 
                    width = 20 
                    height = 50 
                elif enemy.type == "H": 
                    color = "white" # Helicopters 
                    width = 40 
                    height = 25 
                    
                self.create_rectangle( 
                    enemy.x * 30, 
                    enemy.y * 30, 
                    enemy.x * 30 + width, 
                    enemy.y * 30 + height, 
                    fill=color 
                )

        else:
            self.display_game_over()

    def display_game_over(self):
        self.delete("all")
        self.create_text((1000/2), (950/2), text="Game Over", fill="red", font=("Helvetica", 100))
