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
                    self.game_state.game_running = False
                    break

    def _check_missile_enemy_collisions(self):
        for missile in self.game_state.missiles[:]:
            for enemy in self.game_state.enemies[:]:
                if self._is_colliding(missile, enemy):
                    self.game_state.update_score(10)
                    self.game_state.remove_enemy(enemy)
                    self.game_state.remove_missile(missile)
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