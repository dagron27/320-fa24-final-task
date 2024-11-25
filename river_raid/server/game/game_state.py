# server/game/game_state.py
import threading
import logging
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, FuelDepot, Missile
from shared.entity_pool import EntityPool

class GameState:
    """Manages the game's state and entities"""
    STATE_RUNNING = "running"
    STATE_GAME_OVER = "game_over"
    
    def __init__(self):
        self.state_lock = threading.RLock()
        self.entity_pool = EntityPool()
        self.reset()
        
    def reset(self):
        """Reset the game state to initial values"""
        with self.state_lock:
            self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1.5)
            self.missiles = []
            self.fuel_depots = []
            self.enemies = []
            self.score = 0
            self.lives = 3
            self.fuel = 100
            self.game_state = self.STATE_RUNNING
                
    def add_missile(self, missile):
        """Safely add a missile to the game state"""
        with self.state_lock:
            try:
                self.missiles.append(missile)
                logging.debug(f"Missile added at position ({missile.x}, {missile.y})")
            except Exception as e:
                logging.warning(f"Warning in add_missile: {e}")
            
    def add_enemy(self, enemy):
        """Safely add an enemy to the game state"""
        with self.state_lock:
            try:
                self.enemies.append(enemy)
                logging.debug(f"Enemy type {enemy.type} added at position ({enemy.x}, {enemy.y})")
            except Exception as e:
                logging.warning(f"Warning in add_enemy: {e}")
            
    def add_fuel_depot(self, depot):
        """Safely add a fuel depot to the game state"""
        with self.state_lock:
            try:
                self.fuel_depots.append(depot)
                logging.debug(f"Fuel depot added at position ({depot.x}, {depot.y})")
            except Exception as e:
                logging.warning(f"Warning in add_fuel_depot: {e}")
            
    def remove_missile(self, missile):
        """Safely remove a missile and return it to the pool"""
        with self.state_lock:
            try:
                if missile in self.missiles:
                    self.missiles.remove(missile)
                    self.entity_pool.release(missile)
                    logging.debug("Missile removed and returned to pool")
            except Exception as e:
                logging.warning(f"Warning in remove_missile: {e}")
                
    def remove_enemy(self, enemy):
        """Safely remove an enemy and return it to the pool"""
        with self.state_lock:
            try:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.entity_pool.release(enemy)
                    logging.debug(f"Enemy type {enemy.type} removed and returned to pool")
            except Exception as e:
                logging.warning(f"Warning in remove_enemy: {e}")
                
    def remove_fuel_depot(self, depot):
        """Safely remove a fuel depot and return it to the pool"""
        with self.state_lock:
            try:
                if depot in self.fuel_depots:
                    self.fuel_depots.remove(depot)
                    self.entity_pool.release(depot)
                    logging.debug("Fuel depot removed and returned to pool")
            except Exception as e:
                logging.warning(f"Warning in remove_fuel_depot: {e}")
                
    def update_score(self, points):
        """Safely update the game score"""
        with self.state_lock:
            try:
                self.score += points
                logging.debug(f"Score updated: {self.score}")
            except Exception as e:
                logging.warning(f"Warning in update_score: {e}")
            
    def update_fuel(self, amount):
        """Safely update fuel amount and check game over condition"""
        with self.state_lock:
            try:
                self.fuel = max(0, min(100, self.fuel + amount))
                if self.fuel <= 0:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = self.STATE_GAME_OVER
                        logging.info("Game Over - Out of lives")
                    else:
                        self.fuel = 100
                        logging.info(f"Lost life, {self.lives} remaining")
            except Exception as e:
                logging.warning(f"Warning in update_fuel: {e}")
                    
    def get_state(self):
        """Get the current game state for network transmission"""
        with self.state_lock:
            try:
                return {
                    "p": {  # Player
                        "x": self.player.x,
                        "y": self.player.y
                    },
                    "e": [{  # Enemies
                        "x": enemy.x,
                        "y": enemy.y,
                        "t": enemy.type
                    } for enemy in self.enemies],
                    "f": [{  # Fuel depots
                        "x": depot.x,
                        "y": depot.y
                    } for depot in self.fuel_depots],
                    "m": [{  # Missiles
                        "x": missile.x,
                        "y": missile.y,
                        "t": missile.missile_type
                    } for missile in self.missiles],
                    "s": self.score,
                    "l": self.lives,
                    "u": self.fuel,
                    "g": self.game_state
                }
            except Exception as e:
                logging.error(f"Error in get_state: {e}")
                return {}

    def is_running(self):
        """Check if game is running"""
        with self.state_lock:
            return self.game_state == self.STATE_RUNNING

    def is_game_over(self):
        """Check if game is over"""
        with self.state_lock:
            return self.game_state == self.STATE_GAME_OVER