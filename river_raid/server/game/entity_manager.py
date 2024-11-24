import random
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import FuelDepot, EnemyB, EnemyJ, EnemyH

class EntityManager:
    """Handles entity creation, updates and removal"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.SPAWN_RATES = {
            'fuel': 0.05,
            'enemy': 0.1
        }

    def update_enemies(self):
        """Update and manage enemies"""
        with self.game_state.state_lock:
            if random.random() < self.SPAWN_RATES['enemy']:
                x = random.randint(0, int(BOARD_WIDTH) - 1)
                enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
                self.game_state.add_enemy(enemy_type(x, 0, self.game_state))  # Ensure game_state is passed

            for enemy in self.game_state.enemies[:]:
                enemy.move()

                if not enemy.running:
                    self.game_state.remove_enemy(enemy)

    def update_missiles(self):
        """Update and manage missiles"""
        with self.game_state.state_lock:
            for missile in self.game_state.missiles[:]:
                missile.move()
                if missile.y < -1:
                    self.game_state.remove_missile(missile)

    def update_fuel_depots(self):
        """Update and manage fuel depots"""
        with self.game_state.state_lock:
            if random.random() < self.SPAWN_RATES['fuel']:
                self.game_state.add_fuel_depot(
                    FuelDepot(random.randint(0, int(BOARD_WIDTH) - 1), 0)
                )
            for depot in self.game_state.fuel_depots[:]:
                depot.move()
                if depot.y >= BOARD_HEIGHT + 3:
                    self.game_state.remove_fuel_depot(depot)
