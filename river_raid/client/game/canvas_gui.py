import tkinter as tk
from shared.config import CANVAS_WIDTH, CANVAS_HEIGHT, SCALE

class GameCanvas(tk.Canvas):
    def __init__(self, parent, game_logic):
        super().__init__(parent, width=1000, height=950, bg="gray")
        self.game_logic = game_logic
        self.scale = SCALE  # Define scaling factor
        self.width = CANVAS_WIDTH
        self.height = CANVAS_HEIGHT
        self.pack()

    def update_canvas(self):
        self.delete("all")
        if self.game_logic.game_state == "running":
            # Draw player
            self._draw_entity(self.game_logic.player)

            # Draw fuel depots
            for depot in self.game_logic.fuel_depots:
                self._draw_entity(depot)

            # Draw missiles
            for missile in self.game_logic.missiles:
                self._draw_missile(missile)

            # Draw enemies
            for enemy in self.game_logic.enemies:
                self._draw_entity(enemy)
        else:
            self.display_game_over()

    def _draw_entity(self, entity):
        """Draw a rectangular entity (player, enemies, fuel depots)"""
        self.create_rectangle(
            entity.x * self.scale,
            entity.y * self.scale,
            entity.x * self.scale + entity.width,
            entity.y * self.scale + entity.height,
            fill=entity.color
        )

    def _draw_missile(self, missile):
        """Draw a missile as a vertical line"""
        center_x = missile.x * self.scale + (missile.width / 2)
        self.create_line(
            center_x,
            missile.y * self.scale,
            center_x,
            missile.y * self.scale + missile.height,
            fill=missile.color,
            width=missile.width
        )

    def display_game_over(self):
        """Display game over screen"""
        self.delete("all")
        self.create_text(
            self.width / 2,
            self.height / 2,
            text="Game Over",
            fill="red",
            font=("Helvetica", 100)
        )