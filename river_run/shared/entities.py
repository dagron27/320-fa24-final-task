import threading
import time
from shared.config import BOARD_WIDTH, BOARD_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fuel = 100
        self.lives = 3
        self.speed = 1  # Game speed
        self.missile_type = "straight"

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
    lock = threading.Lock()  # Lock for synchronizing access to shared resources

    def __init__(self, x, y, enemy_type, game_logic):
        super().__init__()
        self.x = x
        self.y = y
        self.type = enemy_type
        self.game_logic = game_logic
        self.running = True

    def run(self):
        while self.running:
            with Enemy.lock:
                self.move()
            time.sleep(1)  # Adjust sleep time to slow down enemy behavior

    def move(self):
        raise NotImplementedError("This method should be overridden by subclasses")

class EnemyB(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "B", game_logic)

    def move(self):
        self.y += 1  # Boats move down the river
        if self.y > BOARD_HEIGHT:
            self.running = False

class EnemyJ(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "J", game_logic)
        self.direction = 0  # Jets can move diagonally

    def move(self):
        self.y += 1.5  # Jets move faster
        self.x += self.direction
        if self.y > BOARD_HEIGHT:
            self.running = False

class EnemyH(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "H", game_logic)
        self.direction = 0  # Helicopters can hover and move in any direction

    def move(self):
        self.y += 1  # Helicopters move vertically
        self.x += self.direction  # They can also move horizontally
        if self.y > BOARD_HEIGHT:
            self.running = False

class FuelDepot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y += 1

class Missile:
    def __init__(self, x, y, missile_type):
        self.x = x
        self.y = y
        self.missile_type = missile_type

    def move(self):
        self.y -= 1  # Straight missiles move up
