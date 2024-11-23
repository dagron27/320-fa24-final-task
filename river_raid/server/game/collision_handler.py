from game.game_state import GameState

class CollisionHandler:
    """Handles all collision detection and resolution"""
    def __init__(self, game_state):
        self.game_state = game_state

    def check_all_collisions(self):
        """Check and handle all possible collisions"""
        self._check_player_enemy_collisions()
        self._check_missile_enemy_collisions()
        self._check_player_fuel_collisions()

    def _check_player_enemy_collisions(self):
        for enemy in self.game_state.enemies[:]:
            if self._is_colliding(self.game_state.player, enemy):
                self.game_state.lives -= 1
                self.game_state.remove_enemy(enemy)
                if self.game_state.lives <= 0:
                    self.game_state.game_state = GameState.STATE_GAME_OVER
                    break

    def _check_missile_enemy_collisions(self):
        """Check for collisions between missiles and enemies"""
        with self.game_state.state_lock:
            # Filter out None missiles first
            valid_missiles = [m for m in self.game_state.missiles if m is not None]
            
            for missile in valid_missiles:
                for enemy in self.game_state.enemies[:]:  # Copy list for safe removal
                    if enemy is not None and self._is_colliding(missile, enemy):
                        # Handle collision...
                        self.game_state.score += enemy.points
                        self.game_state.missiles.remove(missile)
                        self.game_state.enemies.remove(enemy)
                        break

    def _check_player_fuel_collisions(self):
        for depot in self.game_state.fuel_depots[:]:
            if self._is_colliding(self.game_state.player, depot):
                self.game_state.update_fuel(50)
                self.game_state.remove_fuel_depot(depot)

    def _is_colliding(self, entity1, entity2):
        width1 = getattr(entity1, 'width', 30) / 30
        height1 = getattr(entity1, 'height', 30) / 30
        width2 = getattr(entity2, 'width', 30) / 30
        height2 = getattr(entity2, 'height', 30) / 30
        
        return (entity1.x < entity2.x + width2 and
                entity1.x + width1 > entity2.x and
                entity1.y < entity2.y + height2 and
                entity1.y + height1 > entity2.y)