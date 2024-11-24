# server/game/collision_handler.py
import logging
from game.game_state import GameState
from shared.config import SCALE

class CollisionHandler:
    """Handles all collision detection and resolution"""
    def __init__(self, game_state):
        self.game_state = game_state

    def check_all_collisions(self):
        """Check and handle all possible collisions"""
        try:
            self._check_player_enemy_collisions()
            self._check_missile_enemy_collisions()
            self._check_player_fuel_collisions()
        except Exception as e:
            logging.warning(f"Warning in check_all_collisions: {e}")

    def _check_player_enemy_collisions(self):
        try:
            for enemy in self.game_state.enemies[:]:
                if self._is_colliding(self.game_state.player, enemy):
                    self.game_state.lives -= 1
                    self.game_state.remove_enemy(enemy)
                    if self.game_state.lives <= 0:
                        self.game_state.game_state = GameState.STATE_GAME_OVER
                        break
        except Exception as e:
            logging.warning(f"Warning in _check_player_enemy_collisions: {e}")

    def _check_missile_enemy_collisions(self):
        try:
            for missile in self.game_state.missiles[:]:
                for enemy in self.game_state.enemies[:]:
                    if self._is_colliding(missile, enemy):
                        self.game_state.update_score(10)
                        self.game_state.remove_enemy(enemy)
                        self.game_state.remove_missile(missile)
                        break
        except Exception as e:
            logging.warning(f"Warning in _check_missile_enemy_collisions: {e}")

    def _check_player_fuel_collisions(self):
        try:
            for depot in self.game_state.fuel_depots[:]:
                if self._is_colliding(self.game_state.player, depot):
                    self.game_state.update_fuel(50)
                    self.game_state.remove_fuel_depot(depot)
        except Exception as e:
            logging.warning(f"Warning in _check_player_fuel_collisions: {e}")

    def _is_colliding(self, entity1, entity2):
        try:
            width1 = getattr(entity1, 'width', SCALE) / SCALE
            height1 = getattr(entity1, 'height', SCALE) / SCALE
            width2 = getattr(entity2, 'width', SCALE) / SCALE
            height2 = getattr(entity2, 'height', SCALE) / SCALE
            
            return (entity1.x < entity2.x + width2 and
                    entity1.x + width1 > entity2.x and
                    entity1.y < entity2.y + height2 and
                    entity1.y + height1 > entity2.y)
        except Exception as e:
            logging.warning(f"Warning in _is_colliding: {e}")
            return False