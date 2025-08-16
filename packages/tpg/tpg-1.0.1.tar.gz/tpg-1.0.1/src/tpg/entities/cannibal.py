from __future__ import annotations
import random

from tpg import entities, game, squares

from tpg.entities.entity import Entity

from PySide6 import QtGui


class Cannibal(Entity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
    ):
        super().__init__(
            game,
            x,
            y,
            valid_squares=[squares.Land],  # cannibal can only move on land
            invalid_squares=[Cannibal],  # cannibal can't move on top of other cannibals
            player_interact_radius=0,  # cannibal can only interact with player if on top of it
        )

        self.brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))  # blue

        self.visible = self.game.cannibal_visible

    @property
    def speed(self) -> int:
        return 1

    def do_turn(self, was_p_move_valid: bool):
        self.check_eat()  # check if adjacent player can be eaten
        direction = squares.directions_corners
        direction = random.choice(direction)
        self.move(direction)  # move in a random direction

        self.check_eat()  # check if player can be eaten after moving

    def check_eat(self):
        for player in self.game.entities.player.get_enabled_players():
            if player.on_top_of(self):  # if player is on top of cannibal
                self.eat(player)  # eat the player

        for tribe in self.game.entities.get_enabled_npcs_t(entities.tribe.Tribe):
            if tribe.on_top_of(self):  # if tribe is on top of cannibal
                self.game.entities.eat_tribe(self, tribe)  # eat the tribe

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        self.check_eat()  # check if player can be eaten after it moves
        res = super().on_player_move(player)
        if not res:
            return False

        if not player.can_be_eated:
            return False

        self.eat(player)  # eat the player if it can be eaten
        return True

    def on_move_one_success(
        self, new: tuple[int, int], old: tuple[int, int], direction: tuple[int, int]
    ):
        self.check_eat()  # check if player can be eaten after moving

    def eat(self, player: entities.player.PlayerEntity):
        self.game.entities.eat_player(self, player)
