# client/game/game_app.py
import tkinter as tk
import time
from game.game_logic import ClientGameLogic
from game.canvas_gui import GameCanvas
from game.game_state import GameState

class GameApp(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("River Raid")
        self.geometry("1000x1000")

        # Initialize game state and logic
        self.game_state = GameState(client)
        self.game_logic = ClientGameLogic(self.game_state)

        # Create canvas and GUI elements
        self.canvas = GameCanvas(self, self.game_logic)
        self.info_label = tk.Label(
            self, 
            text="Score: 0 | Lives: 3 | Fuel: 100",
            font=("Helvetica", 25)
        )
        self.info_label.pack()

        # Bind keyboard controls
        self.bind("<Left>", lambda event: self.player_move("left"))
        self.bind("<Right>", lambda event: self.player_move("right"))
        self.bind("<space>", lambda event: self.player_shoot())
        self.bind("<Return>", lambda event: self.restart_game() if self.game_logic.game_state != "running" else None)
        self.bind("<q>", lambda event: self.quit_game())

        # Configure window close behavior
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Set up game loop
        self.frame_rate = 60  # Target FPS
        self.frame_time = int(1000 / self.frame_rate)  # milliseconds per frame
        self.game_loop()

    def player_move(self, direction):
        """Handle player movement input"""
        if (self.game_logic.game_state == "running" and 
            self.game_logic.player.can_move()):
            self.game_state.send_action({
                "action": "move",
                "direction": direction
            })
            
    def player_shoot(self):
        """Handle player shoot input"""
        if (self.game_logic.game_state == "running" and 
            self.game_logic.player.can_shoot()):
            # Only send shoot action if cooldown check passes
            self.game_state.send_action({
                "action": "shoot"
            })

    def game_loop(self):
        """Main game loop"""
        try:
            # Process any pending state updates
            updates = self.game_state.get_state_updates()
            if updates:
                latest_state = updates[-1]
                self.game_logic.update_game_state(latest_state)

            # Always update canvas and UI every frame
            if self.game_logic.game_state != "running":
                self.canvas.display_game_over()
            else:
                self.canvas.update_canvas()

            # Update game info display
            self.info_label.config(
                text=f"Score: {self.game_logic.score} | Lives: {self.game_logic.lives} | Fuel: {self.game_logic.fuel}",
                font=("Helvetica", 25)
            )

        except Exception as e:
            print(f"Error in game loop: {e}")

        finally:
            # Schedule next frame using constant frame time
            self.after(self.frame_time, self.game_loop)

    def restart_game(self):
        """Handle game restart"""
        self.game_state.send_action({
            "action": "reset_game"
        })
        
        # Local reset
        self.game_logic.reset_game()
        self.info_label.config(
            text="Score: 0 | Lives: 3 | Fuel: 100",
            font=("Helvetica", 25)
        )
        self.canvas.update_canvas()  # Force immediate canvas update

    def quit_game(self):
        """Clean up and close the game"""
        try:
            print("Shutting down game...")
            if hasattr(self, 'game_state'):
                self.game_state.stop()
            self.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.destroy()