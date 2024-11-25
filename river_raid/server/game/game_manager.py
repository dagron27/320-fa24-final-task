# server/game/game_manager.py
import os 
import threading
import queue
import time
import logging
from game.game_state import GameState
from game.game_loops import GameLoops
from game.entity_manager import EntityManager

class GameManager:
    """Manages game state and threads"""
    def __init__(self):
        self.shared_state = GameState()
        self.running = False
        self.game_running = False
        self.input_queue = queue.Queue()
        self._setup_managers_and_threads()

    def _setup_managers_and_threads(self):
        """Initialize managers and setup all threads"""
        # Initialize managers
        self.game_loops = GameLoops(self.shared_state)
        self.entity_manager = EntityManager(self.shared_state)

        # Create threads
        self.threads = {
            'collision': threading.Thread(
                target=self.game_loops.collision_loop,
                args=(self._is_game_running,)
            ),
            'state': threading.Thread(
                target=self.game_loops.state_loop,
                args=(self._is_game_running,)
            ),
            'input': threading.Thread(
                target=self._input_loop
            )
        }

        # Set all threads as daemon
        for thread in self.threads.values():
            thread.daemon = True

    def start(self):
        """Start game manager and all threads"""
        if not self.running:
            self.running = True
            self.game_running = True
            
            # Start all threads
            for thread in self.threads.values():
                thread.start()
                
            # Start enemy movement threads
            self.entity_manager.start_movement_threads()
            logging.info("Game manager started successfully")

    def stop(self):
        """Stop game manager and cleanup"""
        logging.info("Stopping game manager...")
        self.running = False
        self.game_running = False

        # Stop enemy movement threads
        self.entity_manager.stop_movement_threads()

        # Wait for all threads to finish
        for name, thread in self.threads.items():
            if thread.is_alive():
                logging.info(f"Waiting for {name} thread to finish...")
                thread.join()

        logging.info("Game manager stopped successfully")
        os._exit(0)

    def _input_loop(self):
        """Handle input queue processing"""
        while self.running:
            try:
                message = self.input_queue.get(timeout=0.05)
                with self.shared_state.state_lock:
                    if message["action"] == "reset_game":
                        self._handle_reset()
                    elif self.shared_state.game_state == GameState.STATE_RUNNING:
                        self._handle_action(message)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error in input loop: {e}")

    def _handle_reset(self):
        """Handle game reset"""
        self.shared_state.reset()
        self.game_running = True

    def _handle_action(self, message):
        """Handle game actions"""
        try:
            if message["action"] == "move":
                self.shared_state.player.move(message["direction"])
            elif message["action"] == "shoot":
                missile = self.shared_state.player.shoot()
                self.shared_state.add_missile(missile)
        except Exception as e:
            logging.error(f"Error handling action: {e}")

    def process_message(self, message):
        """Process incoming messages"""
        try:
            if message == {'action': 'reset_game'}:
                self._handle_reset()
            else:
                self.input_queue.put(message)
            return {"status": "ok", "game_state": self.shared_state.get_state()}
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            return {"status": "error", "message": str(e)}

    def _is_game_running(self):
        """Check if game is running"""
        return self.game_running