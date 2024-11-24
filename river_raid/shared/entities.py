import threading
import time
import random
from shared.config import SCALE, BOARD_WIDTH, BOARD_HEIGHT, CANVAS_HEIGHT, CANVAS_WIDTH

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fuel = 100
        self.lives = 3
        self.speed = 1
        self.missile_type = "straight"
        self.width = SCALE
        self.height = SCALE
        self.color = "blue"

    def move(self, direction):
        if direction == "left":
            self.x = max(0, self.x - 1)
        elif direction == "right":
            self.x = min(BOARD_WIDTH - 1, self.x + 1)
        elif direction == "accelerate":
            self.speed = min(3, self.speed + 1)
        elif direction == "decelerate":
            self.speed = max(1, self.speed - 1)

    def shoot(self):
        return Missile(self.x + 0.5, self.y - 1, self.missile_type)

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
        self.width = SCALE
        self.height = SCALE
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
        self.width = SCALE * 3
        self.height = SCALE
        self.color = "purple"
        self.vertical_direction = 1  # Start moving left or right randomly 
        self.horizontal_direction = 1  # Start moving left or right randomly 
        self.vertical_speed = 0.5
        self.horizontal_speed = random.uniform(-1, 1)

    def move(self): 
        self.y += self.vertical_direction * self.vertical_speed  # Boats move down the river
    
        # Horizontal movement logic 
        self.x += self.horizontal_direction * self.horizontal_speed 

        # Change direction at boundaries with a threshold 
        if self.x < 0: 
            self.horizontal_direction = 1 # Change direction to right 
        elif self.x + self.width > BOARD_WIDTH: 
            self.horizontal_direction = -1 # Change direction to left

        # Termination condition based on new limits 
        if self.y > BOARD_HEIGHT + SCALE: 
            print(f"B Stopped at x: {self.x} and y: {self.y}") 
            self.running = False

class EnemyJ(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "J", game_logic)
        self.width = SCALE * 1.5
        self.height = SCALE * 2
        self.color = "orange"
        self.direction = random.uniform(1, 2)

    def move(self):
        self.y += self.direction  # Jets move faster
        # Termination condition based on new limits 
        if self.y > BOARD_HEIGHT + SCALE:
            print(f"J Stopped at x: {self.x} and y: {self.y}") 
            self.running = False

class EnemyH(Enemy):
    def __init__(self, x, y, game_logic):
        super().__init__(x, y, "H", game_logic)
        self.width = SCALE * 2
        self.height = SCALE * 0.75
        self.color = "white"
        self.vertical_direction = 1  # Start moving left or right randomly 
        self.horizontal_direction = 1  # Start moving left or right randomly 
        self.vertical_speed = random.uniform(0, 2)
        self.horizontal_speed = random.uniform(-2, 2)

    def move(self):
        self.y += self.vertical_direction * self.vertical_speed
        self.x += self.horizontal_direction * self.horizontal_direction
        
        if(random.randrange(0, 9) > 7):
            self.y += self.vertical_direction * random.uniform(0, 2)
            self.x += self.horizontal_direction * random.uniform(-2, 2)          

        # Termination condition based on new limits 
        if self.y > BOARD_HEIGHT + 50: 
            print(f"H Stopped at x: {self.x} and y: {self.y}") 
            self.running = False

class FuelDepot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = SCALE * 0.75
        self.height = SCALE * 0.75
        self.color = "green"

    def move(self):
        self.y += 1
        if self.y < BOARD_HEIGHT + SCALE: 
            self.running = False

class Missile:
    def __init__(self, x, y, missile_type):
        self.x = x
        self.y = y
        self.missile_type = missile_type
        self.width = SCALE * 0.05
        self.height = SCALE * 0.5
        self.color = "yellow"

    def move(self):
        self.y -= 1  # Straight missiles move up
        # Termination condition based on new limits (5 units above the top of the canvas) 
        if self.y < -SCALE: 
            self.running = False