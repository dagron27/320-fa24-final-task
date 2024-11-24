import random
from shared.config import BOARD_WIDTH, BOARD_HEIGHT, CANVAS_HEIGHT, CANVAS_WIDTH, SCALE
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
        if random.random() < self.SPAWN_RATES['enemy']:
            x = random.randint(0, int(BOARD_WIDTH) - 1)
            enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
            print(enemy_type)
            self.game_state.add_enemy(enemy_type(x, 0, self.game_state))  # Ensure game_state is passed

        for enemy in self.game_state.enemies[:]:
            enemy.move()  # Call the move method for each enemy

            # Remove enemy if it goes out of bounds or stops running
            if not enemy.running:
                print("Enemy removed")
                self.game_state.remove_enemy(enemy)

    def update_missiles(self):
        """Update and manage missiles"""
        for missile in self.game_state.missiles[:]:
            missile.move()
            if missile.y < -SCALE:
                self.game_state.remove_missile(missile)

    def update_fuel_depots(self):
        """Update and manage fuel depots"""
        if random.random() < self.SPAWN_RATES['fuel']:
            self.game_state.add_fuel_depot(
                FuelDepot(random.randint(0, int(BOARD_WIDTH) - 1), 0)
            )
        for depot in self.game_state.fuel_depots[:]:
            depot.move()
            if depot.y >= CANVAS_HEIGHT + SCALE:
                self.game_state.remove_fuel_depot(depot)