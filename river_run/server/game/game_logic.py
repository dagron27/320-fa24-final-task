import random
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, FuelDepot, Missile, EnemyB, EnemyJ, EnemyH

class ServerGameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.missiles = []
        self.fuel_depots = []
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.fuel = 100
        self.game_running = True

    def update_game_state(self):
        if not self.game_running:
            return

        # Add new fuel depots and enemies
        if random.random() < 0.05:
            self.fuel_depots.append(FuelDepot(random.randint(0, BOARD_WIDTH - 1), 0))
        if random.random() < 0.1:
            enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
            self.enemies.append(enemy_type(random.randint(0, BOARD_WIDTH - 1), 0))

        # Move fuel depots, missiles, and enemies
        for depot in self.fuel_depots:
            depot.move()
        for missile in self.missiles:
            missile.move()
        for enemy in self.enemies:
            enemy.move()

        # Check collisions and update game state
        self.check_collisions()

        # Decrease fuel and check game over conditions
        self.fuel -= 1
        if self.fuel <= 0:
            self.lives -= 1
            self.fuel = 100
            if self.lives == 0:
                self.game_running = False

        self.score += 1

    def check_collisions(self):
        for enemy in self.enemies:
            if enemy.x == self.player.x and enemy.y == self.player.y:
                print(f"Collision detected with enemy at ({enemy.x}, {enemy.y}) and player at ({self.player.x}, {self.player.y})")
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives == 0:
                    self.game_running = False
                break

        for depot in self.fuel_depots:
            if depot.x == self.player.x and depot.y == self.player.y:
                print(f"Collision detected with fuel at ({depot.x}, {depot.y}) and enemy at ({self.player.x}, {self.player.y})")
                self.fuel = min(100, self.fuel + 50)
                self.fuel_depots.remove(depot)

        for missile in self.missiles:
            for enemy in self.enemies:
                if missile.x == enemy.x and missile.y == enemy.y:
                    print(f"Collision detected with missile at ({missile.x}, {missile.y}) and enemy at ({enemy.x}, {enemy.y})")
                    self.score += 10
                    self.enemies.remove(enemy)
                    self.missiles.remove(missile)
                    break

        self.enemies = [enemy for enemy in self.enemies if enemy.y < BOARD_HEIGHT]
        self.missiles = [missile for missile in self.missiles if missile.y >= 0]
        self.fuel_depots = [depot for depot in self.fuel_depots if depot.y < BOARD_HEIGHT]

    def process_message(self, message):
        action = message.get("action")
        if action == "move":
            self.player.move(message["direction"])
        elif action == "shoot":
            missile = self.player.shoot()
            self.missiles.append(missile)
        
        # Update game state after processing the action
        self.update_game_state()
        return {"status": "ok", "game_state": self.get_game_state()}

    def get_game_state(self):
        return {
            "player": {"x": self.player.x, "y": self.player.y},
            "enemies": [{"x": enemy.x, "y": enemy.y, "type": enemy.type} for enemy in self.enemies],
            "fuel_depots": [{"x": depot.x, "y": depot.y} for depot in self.fuel_depots],
            "missiles": [{"x": missile.x, "y": missile.y, "type": missile.missile_type} for missile in self.missiles],
            "score": self.score,
            "lives": self.lives,
            "fuel": self.fuel,
            "game_running": self.game_running,
        }
