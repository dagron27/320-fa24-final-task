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
        if random.random() < self.SPAWN_RATES['enemy']:
            x = random.randint(0, BOARD_WIDTH - 1)
            enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
            self.game_state.add_enemy(enemy_type(x, 0, None))

        for enemy in self.game_state.enemies[:]:
            if enemy.type == 'B':
                enemy.y += 1
            elif enemy.type == 'J':
                enemy.y += 1.5
            elif enemy.type == 'H':
                enemy.y += 1
            
            if enemy.y >= BOARD_HEIGHT:
                self.game_state.remove_enemy(enemy)

    def add_missile(self, missile):
        """Add missile to the game state if it's valid"""
        if missile is not None:  # Only add valid missiles
            self.game_state.missiles.append(missile)

    def update_missiles(self):
        """Update all missiles and remove invalid ones"""
        valid_missiles = []
        for missile in self.game_state.missiles:
            if missile is not None:
                missile.move()
                # Keep missiles that are still on screen
                if 0 <= missile.y < BOARD_HEIGHT:
                    valid_missiles.append(missile)
        self.game_state.missiles = valid_missiles

    def update_fuel_depots(self):
        """Update and manage fuel depots"""
        if random.random() < self.SPAWN_RATES['fuel']:
            self.game_state.add_fuel_depot(
                FuelDepot(random.randint(0, BOARD_WIDTH - 1), 0)
            )
        for depot in self.game_state.fuel_depots[:]:
            depot.move()
            if depot.y >= BOARD_HEIGHT:
                self.game_state.remove_fuel_depot(depot)