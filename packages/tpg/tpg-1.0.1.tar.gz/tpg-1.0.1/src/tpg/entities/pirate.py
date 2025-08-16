from __future__ import annotations
import random

from tpg import entities, game, squares

from PySide6 import QtGui


class Pirate(entities.entity.Entity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        move_faster_than_player: bool,
        ransom: float,
    ):
        self.player_safe_spawn_radius = 2  # pirate can't spawn near player

        super().__init__(
            game,
            x,
            y,
            True,
            valid_squares=[squares.Ocean],  # pirate can only move on ocean
            player_interact_radius=1,  # pirate can only interact with player if adjacent
            invalid_squares=[
                Pirate,  # pirate can't move on top of other pirates
                entities.trader.Trader,  # pirate can't move on top of traders
                entities.sea_monster.SeaMonster,  # pirate can't move on top of sea monster
            ],
        )

        self.base_pirate_speed = 1  # base speed of pirate
        self.pirate_boost_speed = 1  # speed boost of pirate above player speed

        self.move_faster_than_player = move_faster_than_player
        self.ransom = ransom

        self.brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))  # black

        self.visible = self.game.pirate_visible

    @property
    def speed(self):
        if self.move_faster_than_player:  # if pirate moves faster than player
            player = self.game.entities.player.get_boat_player()
            if player is not None:
                return (
                    player.speed + self.pirate_boost_speed
                )  # pirate moves faster than player
        return self.base_pirate_speed  # pirate moves at base speed

    def do_turn(self, was_p_move_valid: bool):
        direction = squares.directions_corners
        direction = random.choice(direction)
        self.move(direction)  # move in a random direction

    def on_move_one_success(
        self, new: tuple[int, int], old: tuple[int, int], direction: tuple[int, int]
    ):
        for player in self.game.entities.player.flattened:  # get all players
            if self.player_interact_radius is not None:
                if not player.is_adjacent_to(self, radius=self.player_interact_radius):
                    continue
            if not player.can_plunder:
                continue

            self.plunder(player)  # plunder the player if pirate is adjacent to its

    def plunder(self, player: entities.player.PlayerEntity):
        self.game.entities.plunder_booty(self, player)

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        res = super().on_player_move(
            player
        )  # check if player is within pirate's radius
        if not res:
            return False

        if not player.can_plunder:  # if player can't be plundered
            return False

        self.plunder(player)  # plunder the player if pirate is adjacent to it
        return True

    def valid_square(
        self, square: squares.Square, is_init: bool, ignore_entities: bool = False
    ):
        if not super().valid_square(
            square, is_init
        ):  # check if square is valid for parent
            return False

        if square.is_in_corners(radius=2):  # if square is in corners
            return False

        if is_init:
            for player in self.game.entities.player.get_enabled_players():
                if square.is_adjacent_to(
                    player, radius=self.player_safe_spawn_radius
                ):  # if square is within player's safe spawn radius and the pirate is spawning
                    return False

        return True
