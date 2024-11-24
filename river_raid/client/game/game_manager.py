# client/game/game_manager.py
import tkinter as tk
import logging
import time
from game.game_logic import ClientGameLogic
from game.canvas_gui import GameCanvas
from game.game_state import GameState
from shared.config import WINDOW_HEIGHT, WINDOW_WIDTH

class GameApp(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("River Raid")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

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
        self.bind("<KeyPress-Left>", self.on_key_press)
        self.bind("<KeyRelease-Left>", self.on_key_release)
        self.bind("<KeyPress-Right>", self.on_key_press)
        self.bind("<KeyRelease-Right>", self.on_key_release)
        self.bind("<KeyPress-space>", self.on_key_press)
        self.bind("<KeyRelease-space>", self.on_key_release)
        self.bind("<Return>", lambda event: self.restart_game() if self.game_logic.game_state != "running" else None)
        self.bind("<q>", lambda event: self.quit_game())

        # Key state tracking and cooldowns
        self.keys_pressed = set()
        self.last_move_time = 0
        self.move_cooldown = 0.15  # 200ms cooldown for movement
        self.last_shoot_time = 0
        self.shoot_cooldown = 0.5  # 500ms cooldown for shooting

        # Configure window close behavior
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Set up game loop
        self.tick_rate = 16
        self.game_loop()

    def on_key_press(self, event):
        """Handle key press events"""
        if self.game_logic.game_state == "running":
            self.keys_pressed.add(event.keysym)

    def on_key_release(self, event):
        """Handle key release events"""
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)

    def game_loop(self):
        """Main game loop"""
        try:
            # Process any pending state updates
            updates = self.game_state.get_state_updates()
            if updates:  # Only update if we have new states
                latest_state = updates[-1]  # Use most recent state
                self.game_logic.update_game_state(latest_state)
                self.canvas.update_canvas()

            # Update game info display
            self.info_label.config(
                text=f"Score: {self.game_logic.score} | Lives: {self.game_logic.lives} | Fuel: {self.game_logic.fuel}",
                font=("Helvetica", 25)
            )

            # Handle key states for movement and shooting
            current_time = time.time()
            if "Left" in self.keys_pressed and current_time - self.last_move_time >= self.move_cooldown:
                self.last_move_time = current_time
                self.player_move("left")
            elif "Right" in self.keys_pressed and current_time - self.last_move_time >= self.move_cooldown:
                self.last_move_time = current_time
                self.player_move("right")

            if "space" in self.keys_pressed and current_time - self.last_shoot_time >= self.shoot_cooldown:
                self.last_shoot_time = current_time
                self.player_shoot()

        except Exception as e:
            logging.warning(f"Warning in game_loop: {e}")

        finally:
            # Schedule next frame
            self.after(self.tick_rate, self.game_loop)

    def player_move(self, direction):
        """Handle player movement input"""
        try:
            self.game_state.send_action({
                "action": "move",
                "direction": direction
            })
        except Exception as e:
            logging.warning(f"Warning in player_move: {e}")

    def player_shoot(self):
        """Handle player shoot input"""
        try:
            self.game_state.send_action({
                "action": "shoot"
            })
        except Exception as e:
            logging.warning(f"Warning in player_shoot: {e}")

    def restart_game(self):
        """Handle game restart"""
        try:
            self.canvas.display_game_over()
            # Ensure "Game Over" screen is shown briefly
            self.after(250, self._restart_game)  # Delay reset by 500 milliseconds
        except Exception as e:
            logging.warning(f"Warning in restart_game: {e}")

    def _restart_game(self):
        try:
            self.game_state.send_action({"action": "reset_game"})
            # Local reset
            self.game_logic.reset_game()
            self.info_label.config(
                text="Score: 0 | Lives: 3 | Fuel: 100",
                font=("Helvetica", 25)
            )
        except Exception as e:
            logging.warning(f"Warning in _restart_game: {e}")

    def quit_game(self):
        """Clean up and close the game"""
        try:
            logging.info("Shutting down game...")
            if hasattr(self, 'game_state'):
                self.game_state.stop()
            self.destroy()
        except Exception as e:
            logging.warning(f"Warning during shutdown: {e}")
            self.destroy()