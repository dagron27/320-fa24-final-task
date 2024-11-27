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
        self.entity_pool = EntityPool(max_size=20)  # Reduced pool size

        # Spawn rates and weights
        self.SPAWN_RATES = {
            'enemies': {
                'B': 0.07,  # Adjusted spawn rates
                'J': 0.05,
                'H': 0.03
            },
            'fuel': 0.2
        }

        # Timing controls
        self.spawn_cooldowns = {
            'B': 1.0,    # Time between spawn attempts
            'J': 1.5,
            'H': 2.0,
            'fuel': 3.0
        }
        self.last_spawn_time = {
            'B': 0,
            'J': 0,
            'H': 0,
            'fuel': 0
        }
        
        # Movement timing
        self.movement_interval = 0.2
        self.missile_interval = 0.1
        self.fuel_interval = 0.2        
        self.running = True
        
        # Create threads
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
            if not thread.is_alive():
                thread.daemon = True
                thread.start()
                time.sleep(0.1)  # Ensure thread starts

    def stop_movement_threads(self):
        """Stop all movement threads"""
        self.running = False
        
        for name, thread in self.movement_threads.items():
            if thread.is_alive():
                thread.join(timeout=1.0)
                if thread.is_alive():
                    logging.warning(f"entity_manager: {name} thread did not finish cleanly")
                else:
                    logging.info(f"entity_manager: Stopped {name} thread successfully")

    def _spawner_loop(self):
        """Enhanced spawner loop with cooldowns"""
        while self.running:
            try:
                current_time = time.time()
                
                # Enemy spawning
                for enemy_type, rate in self.SPAWN_RATES['enemies'].items():
                    if (current_time - self.last_spawn_time[enemy_type] >= self.spawn_cooldowns[enemy_type] and 
                        random.random() < rate):
                        
                        # Prepare spawn position outside lock
                        x = random.randint(0, int(BOARD_WIDTH) - 1)
                        
                        # Create entity before state lock
                        enemy = self.entity_pool.acquire(enemy_type, x, 0, self.game_state)
                        
                        # Update game state under lock
                        with self.game_state.state_lock:
                            self.game_state.add_enemy(enemy)
                            self.last_spawn_time[enemy_type] = current_time
                            
            except Exception as e:
                logging.warning(f"entity_manager: Warning in spawner loop: {e}")
            time.sleep(0.1)

    def _process_entity_movement(self, entities, entity_type):
        """Generic entity movement processor"""
        moved_entities = []
        removed_entities = []
        
        for entity in entities:
            entity.move()
            if hasattr(entity, 'running') and not entity.running:
                removed_entities.append(entity)
            else:
                moved_entities.append(entity)
                
        return moved_entities, removed_entities

    def _h_movement_loop(self):
        """Optimized helicopter movement loop"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    h_enemies = [e for e in self.game_state.enemies if e.type == 'H']
                    _, removed = self._process_entity_movement(h_enemies, 'H')
                    for enemy in removed:
                        self.game_state.remove_enemy(enemy)
                        
            except Exception as e:
                logging.warning(f"entity_manager: Warning in H movement loop: {e}")
            time.sleep(self.movement_interval)

    def _j_movement_loop(self):
        """Optimized jet movement loop"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    j_enemies = [e for e in self.game_state.enemies if e.type == 'J']
                    _, removed = self._process_entity_movement(j_enemies, 'J')
                    for enemy in removed:
                        self.game_state.remove_enemy(enemy)
                        
            except Exception as e:
                logging.warning(f"entity_manager: Warning in J movement loop: {e}")
            time.sleep(self.movement_interval)

    def _b_movement_loop(self):
        """Optimized boat movement loop"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    b_enemies = [e for e in self.game_state.enemies if e.type == 'B']
                    _, removed = self._process_entity_movement(b_enemies, 'B')
                    for enemy in removed:
                        self.game_state.remove_enemy(enemy)
                        
            except Exception as e:
                logging.warning(f"entity_manager: Warning in B movement loop: {e}")
            time.sleep(self.movement_interval)

    def _missile_loop(self):
        """Optimized missile movement loop"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    missiles = self.game_state.missiles[:]
                    _, removed = self._process_entity_movement(missiles, 'missile')
                    for missile in removed:
                        self.game_state.remove_missile(missile)
                        
            except Exception as e:
                logging.warning(f"entity_manager: Warning in missile loop: {e}")
            time.sleep(self.missile_interval)

    def _fuel_loop(self):
        """Handle fuel depot spawning and movement"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    current_time = time.time()
                    
                    # Spawn check with cooldown
                    if (current_time - self.last_spawn_time['fuel'] >= self.spawn_cooldowns['fuel'] and
                        random.random() < self.SPAWN_RATES['fuel']):
                        x = random.randint(0, int(BOARD_WIDTH) - 1)
                        depot = self.entity_pool.acquire('fuel', x, 0)
                        self.game_state.add_fuel_depot(depot)
                        self.last_spawn_time['fuel'] = current_time

                    # Move existing fuel depots
                    for depot in self.game_state.fuel_depots[:]:
                        depot.move()
                        if depot.y >= BOARD_HEIGHT + 3:
                            self.game_state.remove_fuel_depot(depot)
                            
            except Exception as e:
                logging.warning(f"entity_manager: Warning in fuel loop: {e}")
            time.sleep(self.fuel_interval)  # Use fuel_interval instead of hard-coded 0.5

    def adjust_spawn_rates(self, difficulty_factor=1.0):
        """Adjust spawn rates based on difficulty"""
        self.SPAWN_RATES['enemies'] = {
            'B': 0.2 * difficulty_factor,
            'J': 0.1 * difficulty_factor,
            'H': 0.1 * difficulty_factor
        }