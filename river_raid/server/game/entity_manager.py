# server/game/entity_manager.py
import logging
import random
import time
import threading
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entity_pool import EntityPool

class EntityManager:
    """Manages all game entities and their movement threads"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.entity_pool = EntityPool()
        
        # Spawn rates and weights
        self.SPAWN_RATES = {
            'enemies': {
                'B': 0.7,  # 70% chance for boats
                'J': 0.5,  # 50% chance for jets
                'H': 0.3   # 30% chance for helicopters
            },
            'fuel': 0.2    # 20% chance for fuel
        }

        self.ENEMY_WEIGHTS = {
            'B': 50,  # Boat: 50% when spawning enemy
            'J': 30,  # Jet: 30% when spawning enemy
            'H': 20   # Helicopter: 20% when spawning enemy
        }

        # Timing intervals
        self.spawn_interval = 1.0  # Check for spawning every second
        self.movement_interval = 0.2  # Move enemies every 0.2 seconds
        self.running = True
        
        # Create threads for each game system
        self.movement_threads = {
            'H': threading.Thread(target=self._h_movement_loop),
            'J': threading.Thread(target=self._j_movement_loop),
            'B': threading.Thread(target=self._b_movement_loop),
            'spawner': threading.Thread(target=self._spawner_loop),
            'missiles': threading.Thread(target=self._missile_loop),
            'fuel': threading.Thread(target=self._fuel_loop)
        }

    def start_movement_threads(self):
        """Start all movement threads"""
        for name, thread in self.movement_threads.items():
            thread.daemon = True
            thread.start()
            logging.info(f"entity_manager: Started {name} thread")
            
    def stop_movement_threads(self):
        """Stop all movement threads"""
        self.running = False
        for name, thread in self.movement_threads.items():
            if thread.is_alive():
                logging.info(f"entity_manager: Stopping {name} thread...")
                thread.join(timeout=1.0)
                if thread.is_alive():
                    logging.warning(f"entity_manager: {name} thread did not finish cleanly")
                else:
                    logging.info(f"entity_manager: Stopped {name} thread successfully")

    def _get_weighted_enemy_type(self):
        """Get enemy type based on weights"""
        total = sum(self.ENEMY_WEIGHTS.values())
        r = random.uniform(0, total)
        cumulative = 0
        
        for enemy_type, weight in self.ENEMY_WEIGHTS.items():
            cumulative += weight
            if r <= cumulative:
                return enemy_type
        return 'B'  # Default to boat if something goes wrong

    def _spawner_loop(self):
        """Dedicated thread for enemy spawning"""
        while self.running:
            try:
                # Check spawning for each enemy type
                for enemy_type, rate in self.SPAWN_RATES['enemies'].items():
                    if random.random() < rate:
                        with self.game_state.state_lock:
                            x = random.randint(0, int(BOARD_WIDTH) - 1)
                            enemy = self.entity_pool.acquire(enemy_type, x, 0, self.game_state)
                            self.game_state.add_enemy(enemy)
                            #logging.info(f"entity_manager: Spawned new {enemy_type} enemy")
            except Exception as e:
                logging.warning(f"entity_manager: Warning in spawner loop: {e}")
            time.sleep(self.spawn_interval)

    def _h_movement_loop(self):
        """Handle helicopter enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    h_enemies = [e for e in self.game_state.enemies if e.type == 'H']
                    for enemy in h_enemies:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"entity_manager: Warning in H movement loop: {e}")
            time.sleep(self.movement_interval)

    def _j_movement_loop(self):
        """Handle jet enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    j_enemies = [e for e in self.game_state.enemies if e.type == 'J']
                    for enemy in j_enemies:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"entity_manager: Warning in J movement loop: {e}")
            time.sleep(self.movement_interval)

    def _b_movement_loop(self):
        """Handle boat enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    b_enemies = [e for e in self.game_state.enemies if e.type == 'B']
                    for enemy in b_enemies:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"entity_manager: Warning in B movement loop: {e}")
            time.sleep(self.movement_interval)

    def _missile_loop(self):
        """Handle missile movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    for missile in self.game_state.missiles[:]:
                        missile.move()
                        if missile.y < -1:
                            self.game_state.remove_missile(missile)
            except Exception as e:
                logging.warning(f"entity_manager: Warning in missile loop: {e}")
            time.sleep(0.05)  # Faster update for smooth missile movement

    def _fuel_loop(self):
        """Handle fuel depot spawning and movement"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    # Spawn new fuel depots
                    if random.random() < self.SPAWN_RATES['fuel']:
                        x = random.randint(0, int(BOARD_WIDTH) - 1)
                        depot = self.entity_pool.acquire('fuel', x, 0)
                        self.game_state.add_fuel_depot(depot)
                        #logging.info("entity_manager: Spawned new fuel depot")

                    # Move existing fuel depots
                    for depot in self.game_state.fuel_depots[:]:
                        depot.move()
                        if depot.y >= BOARD_HEIGHT + 3:
                            self.game_state.remove_fuel_depot(depot)
            except Exception as e:
                logging.warning(f"entity_manager: Warning in fuel loop: {e}")
            time.sleep(1.0)  # Check fuel spawning every second

    def adjust_spawn_rates(self, difficulty_factor=1.0):
        """Adjust spawn rates based on difficulty"""
        self.SPAWN_RATES['enemies'] = {
            'B': 0.2 * difficulty_factor,
            'J': 0.1 * difficulty_factor,
            'H': 0.1 * difficulty_factor
        }