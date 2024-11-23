import time
from game.entity_manager import EntityManager
from game.collision_handler import CollisionHandler

class GameLoops:
    """Handles all game loop logic"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.entity_manager = EntityManager(game_state)
        self.collision_handler = CollisionHandler(game_state)
        
        self.ENEMY_UPDATE_INTERVAL = 0.2
        self.COLLISION_CHECK_INTERVAL = 0.1
        self.STATE_UPDATE_INTERVAL = 0.2

    def enemy_loop(self, running):
        while running():
            with self.game_state.state_lock:
                if not self.game_state.game_running:
                    time.sleep(self.ENEMY_UPDATE_INTERVAL)
                    continue
                self.entity_manager.update_enemies()
            time.sleep(self.ENEMY_UPDATE_INTERVAL)

    def collision_loop(self, running):
        while running():
            with self.game_state.state_lock:
                if not self.game_state.game_running:
                    time.sleep(self.COLLISION_CHECK_INTERVAL)
                    continue
                self.collision_handler.check_all_collisions()
            time.sleep(self.COLLISION_CHECK_INTERVAL)

    def state_loop(self, running):
        fuel_counter = 0
        score_counter = 0
        
        while running():
            with self.game_state.state_lock:
                if not self.game_state.game_running:
                    time.sleep(self.STATE_UPDATE_INTERVAL)
                    continue

                self.entity_manager.update_missiles()
                self.entity_manager.update_fuel_depots()

                # Update counters
                fuel_counter = (fuel_counter + 1) % 5
                score_counter = (score_counter + 1) % 10

                if fuel_counter == 0:
                    self.game_state.update_fuel(-1)
                if score_counter == 0:
                    self.game_state.update_score(1)

            time.sleep(self.STATE_UPDATE_INTERVAL)