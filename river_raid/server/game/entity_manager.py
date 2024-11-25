# server/game/entity_manager.py
import logging
import random
import time
import threading
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import FuelDepot, EnemyB, EnemyJ, EnemyH

class EntityManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.SPAWN_RATES = {
            'enemy': 0.4,  # 40% chance per check
            'fuel': 0.05  # Make sure this rate is defined
        }
        self.spawn_interval = 1.0  # Check for spawning every second
        self.movement_interval = 0.2  # Move enemies every 0.2 seconds
        self.running = True
        
        # Create threads for each enemy type and spawning
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
        for thread in self.movement_threads.values():
            thread.daemon = True
            thread.start()
            
    def stop_movement_threads(self):
        """Stop all movement threads"""
        self.running = False
        for thread in self.movement_threads.values():
            if thread.is_alive():
                thread.join(timeout=1.0)

    def _spawner_loop(self):
        """Dedicated thread for enemy spawning"""
        while self.running:
            try:
                if random.random() < self.SPAWN_RATES['enemy']:
                    with self.game_state.state_lock:
                        x = random.randint(0, int(BOARD_WIDTH) - 1)
                        enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
                        self.game_state.add_enemy(enemy_type(x, 0, self.game_state))
                        logging.info(f"Spawned new {enemy_type.__name__}")
            except Exception as e:
                logging.warning(f"Warning in spawner loop: {e}")
            time.sleep(self.spawn_interval)

    def _h_movement_loop(self):
        """Handle helicopter enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    for enemy in [e for e in self.game_state.enemies if isinstance(e, EnemyH)]:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"Warning in H movement loop: {e}")
            time.sleep(self.movement_interval)

    def _j_movement_loop(self):
        """Handle jet enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    for enemy in [e for e in self.game_state.enemies if isinstance(e, EnemyJ)]:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"Warning in J movement loop: {e}")
            time.sleep(self.movement_interval)

    def _b_movement_loop(self):
        """Handle boat enemy movements"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    for enemy in [e for e in self.game_state.enemies if isinstance(e, EnemyB)]:
                        enemy.move()
                        if not enemy.running:
                            self.game_state.remove_enemy(enemy)
            except Exception as e:
                logging.warning(f"Warning in B movement loop: {e}")
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
                logging.warning(f"Warning in missile loop: {e}")
            time.sleep(0.05)  # Faster update for smooth missile movement

    def _fuel_loop(self):
        """Handle fuel depot spawning and movement"""
        while self.running:
            try:
                with self.game_state.state_lock:
                    # Spawn new fuel depots
                    if random.random() < self.SPAWN_RATES['fuel']:
                        x = random.randint(0, int(BOARD_WIDTH) - 1)
                        self.game_state.add_fuel_depot(FuelDepot(x, 0))
                        logging.info("Spawned new fuel depot")

                    # Move existing fuel depots
                    for depot in self.game_state.fuel_depots[:]:
                        depot.move()
                        if depot.y >= BOARD_HEIGHT + 3:
                            self.game_state.remove_fuel_depot(depot)
            except Exception as e:
                logging.warning(f"Warning in fuel loop: {e}")
            time.sleep(1.0)  # Check fuel spawning every second