import random
from entities import Player, Obstacle, FuelDepot, Missile

BOARD_WIDTH = 10
BOARD_HEIGHT = 10

class GameLogic:
    def __init__(self):
        self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.obstacles = []
        self.missiles = []
        self.fuel_depots = []
        self.score = 0
        self.lives = 3
        self.fuel = 100

    def update_game_state(self):
        # Add new obstacles
        if random.random() < 0.2:
            self.obstacles.append(Obstacle(random.randint(0, BOARD_WIDTH - 1), 0))

        # Add new fuel depots
        if random.random() < 0.05:
            self.fuel_depots.append(FuelDepot(random.randint(0, BOARD_WIDTH - 1), 0))

        # Move obstacles
        for obs in self.obstacles:
            obs.move()

        # Move fuel depots
        for depot in self.fuel_depots:
            depot.move()

        # Move missiles
        for missile in self.missiles:
            missile.move()

        # Check collisions
        self.check_collisions()

        # Decrease fuel
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
