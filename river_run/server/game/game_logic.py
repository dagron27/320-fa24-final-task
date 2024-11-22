import random
import threading
from shared.config import BOARD_WIDTH, BOARD_HEIGHT
from shared.entities import Player, FuelDepot, Missile, EnemyB, EnemyJ, EnemyH

class ServerGameLogic:
    def __init__(self):
        self.game_state_lock = threading.RLock()
        self.reset_game()

    def reset_game(self):
        with self.game_state_lock:
            self.player = Player(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
            self.missiles = []
            self.fuel_depots = []
            self.enemies = []
            self.enemy_threads = []
            self.score = 0
            self.lives = 3
            self.fuel = 100
            self.game_running = True

    def update_game_state(self):
        if not self.game_running:
            return

        with self.game_state_lock:
            if random.random() < 0.05:
                self.fuel_depots.append(FuelDepot(random.randint(0, BOARD_WIDTH - 1), 0))

            if random.random() < 0.1:
                x = random.randint(0, BOARD_WIDTH - 1)
                enemy_type = random.choice([EnemyB, EnemyJ, EnemyH])
                enemy = enemy_type(x, 0, self)
                self.enemies.append(enemy)
                self.enemy_threads.append(enemy)
                enemy.start()

            # Move missiles
            for missile in self.missiles:
                missile.move()

            # Move fuel depots
            for depot in self.fuel_depots:
                depot.move()

            self.check_collisions()

            self.fuel -= 1
            if self.fuel <= 0:
                self.fuel = 0
                self.lives -= 1
                if self.lives <= 0:
                    self.lives = 0
                    self.game_running = False
                else:
                    self.fuel = 100

            self.score += 1

    def check_collisions(self):
        with self.game_state_lock:
            for enemy in self.enemies[:]:
                if self.is_colliding(self.player, enemy):
                    print(f"Collision detected - Enemy Type: {enemy.type} - Player at ({self.player.x}, {self.player.y}) and enemy at ({enemy.x}, {enemy.y})")
                    self.lives -= 1
                    self.enemies.remove(enemy)
                    enemy.running = False
                    if self.lives <= 0:
                        self.lives = 0
                        self.game_running = False
                        for e in self.enemies[:]:
                            e.running = False
                        self.enemies.clear()
                    break

            for depot in self.fuel_depots[:]:
                if self.is_colliding(self.player, depot):
                    self.fuel = min(100, self.fuel + 50)
                    self.fuel_depots.remove(depot)

            for missile in self.missiles[:]:
                for enemy in self.enemies[:]:
                    if self.is_colliding(missile, enemy):
                        print(f"Collision detected - Missile hit Enemy Type: {enemy.type} at ({enemy.x}, {enemy.y})")
                        self.score += 10
                        self.enemies.remove(enemy)
                        enemy.running = False
                        self.missiles.remove(missile)
                        break

            self.enemies = [enemy for enemy in self.enemies if enemy.running]
            self.missiles = [missile for missile in self.missiles if missile.y >= 0]
            self.fuel_depots = [depot for depot in self.fuel_depots if depot.y < BOARD_HEIGHT]

    def is_colliding(self, entity1, entity2):
        width1 = getattr(entity1, 'width', 30) / self.scale
        height1 = getattr(entity1, 'height', 30) / self.scale
        width2 = getattr(entity2, 'width', 30) / self.scale
        height2 = getattr(entity2, 'height', 30) / self.scale
        
        return (entity1.x < entity2.x + width2 and
                entity1.x + width1 > entity2.x and
                entity1.y < entity2.y + height2 and
                entity1.y + height1 > entity2.y)

    def process_message(self, message):
        action = message.get("action")
        
        with self.game_state_lock:
            if action == "move":
                self.player.move(message["direction"])
            elif action == "shoot":
                missile = self.player.shoot()
                self.missiles.append(missile)
            elif action == "reset_game":
                for enemy in self.enemy_threads:
                    enemy.running = False
                self.enemy_threads = []
                self.reset_game()
            elif action == "quit_game":
                self.game_running = False
                for enemy in self.enemy_threads:
                    enemy.running = False
                self.enemy_threads = []

            self.update_game_state()
            return {"status": "ok", "game_state": self.get_game_state()}

    def get_game_state(self):
        with self.game_state_lock:
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

    @property
    def scale(self):
        return 30