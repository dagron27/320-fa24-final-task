import random
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, Obstacle, FuelDepot, Missile

class ServerGameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.obstacles = []
        self.missiles = []
        self.fuel_depots = []
        self.score = 0
        self.lives = 3
        self.fuel = 100
        self.game_running = True

    def update_game_state(self):
        if not self.game_running:
            return

        # Add new obstacles and fuel depots
        if random.random() < 0.2:
            self.obstacles.append(Obstacle(random.randint(0, BOARD_WIDTH - 1), 0, random.randint(-1, 1)))
        if random.random() < 0.05:
            self.fuel_depots.append(FuelDepot(random.randint(0, BOARD_WIDTH - 1), 0))

        # Move obstacles, fuel depots, missiles
        for obs in self.obstacles:
            if (obs.x + obs.direction) < 0 or (obs.x + obs.direction) > (BOARD_WIDTH - 1):
                obs.direction = -obs.direction
            obs.move()
        for depot in self.fuel_depots:
            depot.move()
        for missile in self.missiles:
            missile.move()

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
        for obs in self.obstacles:
            if obs.x == self.player.x and obs.y == self.player.y:
                self.lives -= 1
                self.obstacles.remove(obs)
                if self.lives == 0:
                    self.game_running = False
                break

        for depot in self.fuel_depots:
            if depot.x == self.player.x and depot.y == self.player.y:
                self.fuel = min(100, self.fuel + 50)
                self.fuel_depots.remove(depot)

        for missile in self.missiles:
            for obs in self.obstacles:
                if missile.x == obs.x and missile.y == obs.y:
                    self.score += 10
                    self.obstacles.remove(obs)
                    self.missiles.remove(missile)
                    break

        self.obstacles = [obs for obs in self.obstacles if obs.y < BOARD_HEIGHT]
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
            "obstacles": [{"x": obs.x, "y": obs.y, "direction": obs.direction} for obs in self.obstacles],
            "fuel_depots": [{"x": depot.x, "y": depot.y} for depot in self.fuel_depots],
            "missiles": [{"x": missile.x, "y": missile.y, "type": missile.missile_type} for missile in self.missiles],
            "score": self.score,
            "lives": self.lives,
            "fuel": self.fuel,
            "game_running": self.game_running,
        }
