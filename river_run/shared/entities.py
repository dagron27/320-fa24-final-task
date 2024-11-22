from shared.config import BOARD_WIDTH

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

# class Obstacle:
#     def __init__(self, x, y, direction):
#         self.x = x
#         self.y = y
#         self.direction = direction

#     def move(self):
#         self.y += 1
#         self.x += self.direction

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type

    def move(self):
        raise NotImplementedError("This method should be overridden by subclasses")

class EnemyB(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "B")

    def move(self):
        self.y += 1  # Boats move down the river

class EnemyJ(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "J")
        self.direction = 0  # Jets can move diagonally

    def move(self):
        self.y += 1.5  # Jets move faster
        self.x += self.direction

class EnemyH(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "H")
        self.direction = 0  # Helicopters can hover and move in any direction

    def move(self):
        self.y += 1  # Helicopters move vertically
        self.x += self.direction  # They can also move horizontally

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
