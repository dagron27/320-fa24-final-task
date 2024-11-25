# server/game/game_loops.py
import time
import logging
from game.collision_handler import CollisionHandler

class GameLoops:
    """Handles game loop mechanics and timing"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.collision_handler = CollisionHandler(game_state)
        
        # Constants for timing
        self.FUEL_RATE = 3
        self.SCORE_RATE = 5
        self.COLLISION_CHECK_INTERVAL = 0.05
        self.STATE_UPDATE_INTERVAL = 0.15

    def collision_loop(self, running):
        """Handle collision detection between game entities"""
        while running():
            try:
                with self.game_state.state_lock:
                    if not self.game_state.STATE_RUNNING:
                        time.sleep(self.COLLISION_CHECK_INTERVAL)
                        continue
                        
                    # Check all types of collisions
                    self.collision_handler.check_all_collisions()
                    
            except Exception as e:
                logging.warning(f"Warning in collision loop: {e}")
                
            time.sleep(self.COLLISION_CHECK_INTERVAL)

    def state_loop(self, running):
        """Handle game state updates (score and fuel)"""
        fuel_counter = 0
        score_counter = 0
        
        while running():
            try:
                with self.game_state.state_lock:
                    if not self.game_state.STATE_RUNNING:
                        time.sleep(self.STATE_UPDATE_INTERVAL)
                        continue
                        
                    # Update fuel consumption
                    fuel_counter = (fuel_counter + 1) % self.FUEL_RATE
                    if fuel_counter == 0:
                        self.game_state.update_fuel(-1)
                        logging.debug("Fuel decreased")
                        
                    # Update score
                    score_counter = (score_counter + 1) % self.SCORE_RATE
                    if score_counter == 0:
                        self.game_state.update_score(1)
                        logging.debug(f"Score increased, current: {self.game_state.score}")
                        
            except Exception as e:
                logging.warning(f"Warning in state loop: {e}")
                
            time.sleep(self.STATE_UPDATE_INTERVAL)