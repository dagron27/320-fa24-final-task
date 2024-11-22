import threading
import time
from shared.config import BOARD_WIDTH, BOARD_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fuel = 100
        self.lives = 3
        self.speed = 1
        self.missile_type = "straight"
        self.width = 30
        self.height = 30
        self.color = "blue"

    def move(self, direction):
        if direction == "left":
            self.x = max(0, self.x - 1)
        elif direction == "right":
            self.x = min(BOARD_WIDTH - 0.75, self.x + 1)
        elif direction == "accelerate":
            self.speed = min(3, self.speed + 1)
        elif direction == "decelerate":
            self.speed = max(1, self.speed - 1)

    def shoot(self):
        return Missile(self.x, self.y - 1, self.missile_type)

    def switch_missile(self):
        self.missile_type = "guided" if self.missile_type == "straight" else "straight"

class Enemy(threading.Thread):
    def __init__(self, x, y, enemy_type, game_logic):
        super().__init__()
        self.x = x
        self.y = y
        self.type = enemy_type
        self.game_logic = game_logic
        self.running = True
        self.lock = threading.Lock()
        self.width = 30
        self.height = 30
        self.color = "red"

    def run(self):
        while self.running:
            with self.lock:
                self.move()
            time.sleep(0.2)

    def move(self):
        raise NotImplementedError("This method should be overridden by subclasses")

class EnemyB(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "B", game_logic)
        self.width = 80
        self.height = 20
        self.color = "purple"

    def move(self):
        self.y += 1  # Boats move down the river
        if self.y > BOARD_HEIGHT:
            self.running = False

class EnemyJ(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "J", game_logic)
        self.width = 20
        self.height = 50
        self.color = "orange"
        self.direction = 0

    def move(self):
        self.y += 1.5  # Jets move faster
        self.x += self.direction
        if self.y > BOARD_HEIGHT:
            self.running = False

class EnemyH(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "H", game_logic)
        self.width = 40
        self.height = 25
        self.color = "white"
        self.direction = 0

    def move(self):
        self.y += 1  # Helicopters move vertically
        self.x += self.direction  # They can also move horizontally
        if self.y > BOARD_HEIGHT:
            self.running = False

class FuelDepot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.color = "green"

    def move(self):
        self.y += 1

class Missile:
    def __init__(self, x, y, missile_type):
        self.x = x
        self.y = y
        self.missile_type = missile_type
        self.width = 2
        self.height = 30
        self.color = "yellow"

    def move(self):
        self.y -= 1  # Straight missiles move up