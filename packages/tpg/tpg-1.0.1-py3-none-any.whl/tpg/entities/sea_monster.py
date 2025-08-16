from __future__ import annotations

import random

from tpg import entities, game, squares
from PySide6 import QtGui


class SeaMonster(entities.entity.Entity):
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
            valid_squares=[squares.Ocean],  # sea monster can only move on ocean
            invalid_squares=[
                SeaMonster,  # sea monster can't move on top of other sea monsters
                entities.pirate.Pirate,  # sea monster can't move on top of pirates
                entities.trader.Trader,  # sea monster can't move on top of traders
            ],
            player_interact_radius=0,  # sea monster can only interact with player if on top of it
        )

        self.brush = QtGui.QBrush(QtGui.QColor(255, 0, 255))  # magenta

        self.visible = self.game.sea_monster_visible

    @property
    def speed(self) -> int:
        return 3

    def do_turn(self, was_p_move_valid: bool):
        direction = squares.directions_corners
        direction = random.choice(direction)
        self.move(direction)  # move in a random direction

    def on_move_one_success(
        self, new: tuple[int, int], old: tuple[int, int], direction: tuple[int, int]
    ):
        for player in self.game.entities.player.get_enabled_players():
            if player.on_top_of(self):
                self.eat(player)

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        res = super().on_player_move(player)
        if not res:
            return False

        if not player.can_be_eated:
            return False

        self.eat(player)
        return True

    def eat(self, player: entities.player.PlayerEntity):
        self.game.entities.eat_player(self, player)

    def give_rumour(self) -> tuple[int, int] | None:
        adjacent_sq = list(self.get_adjacent_t(squares.Ocean, radius=5))
        if not adjacent_sq:
            return None

        return random.choice(
            adjacent_sq
        ).pos  # returns a random adjacent ocean square 5 radius
