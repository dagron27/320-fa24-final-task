# server/game/game_loops.py
import logging
import time
from game.entity_manager import EntityManager
from game.collision_handler import CollisionHandler

class GameLoops:
    def __init__(self, game_state):
        self.game_state = game_state
        self.entity_manager = EntityManager(game_state)
        self.collision_handler = CollisionHandler(game_state)

        self.FUEL_RATE = 3
        self.SCORE_RATE = 5

        self.ENEMY_UPDATE_INTERVAL = 0.15
        self.COLLISION_CHECK_INTERVAL = 0.05
        self.STATE_UPDATE_INTERVAL = 0.15

    def enemy_loop(self, running):
        while running():
            try:
                #logging.info("Enemy loop trying to acquire lock")
                with self.game_state.state_lock:
                    #logging.info("Enemy loop acquired lock")
                    if not self.game_state.STATE_RUNNING:
                        time.sleep(self.ENEMY_UPDATE_INTERVAL)
                        continue
                    self.entity_manager.update_enemies()
            except Exception as e:
                logging.warning(f"Warning in enemy_loop: {e}")
            #finally:
                logging.info("Enemy loop releasing lock")
            time.sleep(self.ENEMY_UPDATE_INTERVAL)

    def collision_loop(self, running):
        while running():
            try:
                #logging.info("Collision loop trying to acquire lock")
                with self.game_state.state_lock:
                    #logging.info("Collision loop acquired lock")
                    if not self.game_state.STATE_RUNNING:
                        time.sleep(self.COLLISION_CHECK_INTERVAL)
                        continue
                    self.collision_handler.check_all_collisions()
            except Exception as e:
                logging.warning(f"Warning in collision_loop: {e}")
            #finally:
                #logging.info("Collision loop releasing lock")
            time.sleep(self.COLLISION_CHECK_INTERVAL)

    def state_loop(self, running):
        fuel_counter = 0
        score_counter = 0
        
        while running():
            try:
                #logging.info("State loop trying to acquire lock")
                with self.game_state.state_lock:
                    #logging.info("State loop acquired lock")
                    if not self.game_state.STATE_RUNNING:
                        time.sleep(self.STATE_UPDATE_INTERVAL)
                        continue

                    self.entity_manager.update_missiles()
                    self.entity_manager.update_fuel_depots()

                    # Update counters
                    fuel_counter = (fuel_counter + 1) % self.FUEL_RATE
                    score_counter = (score_counter + 1) % self.SCORE_RATE

                    if fuel_counter == 0:
                        self.game_state.update_fuel(-1)
                    if score_counter == 0:
                        self.game_state.update_score(1)
            except Exception as e:
                logging.warning(f"Warning in state_loop: {e}")
            #finally:
                #logging.info("State loop releasing lock")
            time.sleep(self.STATE_UPDATE_INTERVAL)