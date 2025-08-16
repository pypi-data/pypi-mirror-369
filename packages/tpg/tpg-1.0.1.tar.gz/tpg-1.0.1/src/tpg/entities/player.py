from __future__ import annotations

import random
from typing import Generator, TypeVar

from tpg import entities, game, squares, upgrade

from PySide6 import QtGui


class PlayerEntity(entities.entity.Entity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        enabled: bool = True,
        can_move_on: list[type[squares.Square]] | None = None,
        cant_move_on: list[type[squares.Square]] | None = None,
        can_plunder: bool = True,
    ):
        super().__init__(game, x, y, enabled, can_move_on, cant_move_on)
        self.can_plunder = can_plunder
        self.can_be_eated = True

    def move_one(self, direction: tuple[int, int]) -> bool:
        res = super().move_one(direction)
        if not res:
            return False

        self.call_on_player_move()
        return True

    def call_on_player_move(self):
        for entity in self.game.entities.get_enabled_npcs():
            entity.on_player_move(self)  # call on_player_move for all enabled npcs


class BoatPlayer(PlayerEntity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        enabled: bool = True,
    ):
        super().__init__(
            game, x, y, enabled, cant_move_on=[squares.Land], can_plunder=True
        )

        self.brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))  # red

    @property
    def speed(self) -> int:
        if self.game.entities.player.has_upgrade(upgrade.UpgradeType.BIGGER_SAIL):
            return 3
        return 2


class LandPlayer(PlayerEntity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        enabled: bool = True,
    ):
        super().__init__(
            game, x, y, enabled, cant_move_on=[squares.Water], can_plunder=False
        )

        self.brush = QtGui.QBrush(QtGui.QColor(128, 0, 0))  # dark red

        self.visible = False

    @property
    def speed(self) -> int:
        if self.game.entities.player.has_upgrade(upgrade.UpgradeType.MAP_READING):
            return 2
        return 1


class Player:
    def __init__(
        self,
        game: game.Game,
    ):
        self.game = game

        self.__player_states: dict[type, list[PlayerEntity]] = (
            {}
        )  # this has extra support for multiple player states for each type but is not used

        self.__flattened: list[PlayerEntity] = []

        self.gold = 0

        self.upgrades: list[bool] = [False] * len(upgrade.UpgradeType)

    def has_upgrade(self, type: upgrade.UpgradeType):
        return self.upgrades[type.value]

    def is_in_corner(self):
        player: PlayerEntity | None = None
        if self.on_land():
            player = self.get_land_player()
        else:
            player = self.get_boat_player()

        if player is None:
            return False

        return player.is_in_corners(radius=2)  # check if player is in corners

    def try_upgrade(self, upgrade: upgrade.Upgrade) -> str | None:
        if not self.is_in_corner():
            return "You are not in the corners of the board!"
        if self.has_upgrade(upgrade.type):
            return "You already have this upgrade!"
        if self.gold < upgrade.cost:
            return "You cannot afford this upgrade!"
        self.remove_gold(upgrade.cost)
        self.upgrades[upgrade.type.value] = True
        return None

    def flatten(self):
        """Flatten the player states into a single list."""
        self.__flattened = []
        for states in self.__player_states.values():
            self.__flattened.extend(states)

    @property
    def flattened(self) -> list[PlayerEntity]:
        return self.__flattened

    def add_player(self, player: PlayerEntity):
        p_type = type(player)
        states = self.__player_states.get(p_type)
        if states is None:
            self.__player_states[p_type] = [player]
        else:
            states.append(player)

        self.__flattened.append(player)

    def get_player_t_many(self, t: type[P]) -> list[P]:
        states = self.__player_states.get(t, [])
        return states  # type: ignore

    def get_player_t(self, t: type[P]) -> P | None:
        """Get the first player of type t.

        Args:
            t (type[P]): The type of player to get.

        Returns:
            P | None: The player of type t or None if not found.
        """
        states = self.get_player_t_many(t)
        if not states:
            return None
        return states[0]

    def get_boat_player(self) -> BoatPlayer | None:
        return self.get_player_t(BoatPlayer)

    def get_land_player(self) -> LandPlayer | None:
        return self.get_player_t(LandPlayer)

    def get_enabled_players(self) -> Generator[PlayerEntity, None, None]:
        for states in self.__player_states.values():
            for entity in states:
                if entity.enabled:
                    yield entity

    def get_enabled_player(self) -> PlayerEntity | None:
        return next(self.get_enabled_players(), None)

    def on_land(self) -> bool:
        land_player = self.get_land_player()
        if land_player is None:
            return False

        return land_player.enabled

    def set_on_land(self, on_land: bool) -> tuple[bool, bool]:
        boat_player = self.get_boat_player()
        land_player = self.get_land_player()

        if boat_player is None or land_player is None:
            return False, False

        if on_land:
            if not boat_player.enabled or land_player.enabled:
                return False, False
            land_adjacents = list(boat_player.get_adjacent_t(squares.Land))
            if not land_adjacents:
                return False, True

            square = random.choice(
                land_adjacents
            )  # disembark on a random adjacent land square
            land_player.x = square.x
            land_player.y = square.y
        else:
            if boat_player.enabled or not land_player.enabled:
                return False, False
            if not land_player.is_adjacent_to(boat_player):
                return False, False

        land_player.enabled = on_land
        land_player.visible = on_land
        boat_player.enabled = not on_land

        if land_player.enabled:
            land_player.call_on_player_move()
        if boat_player.enabled:
            boat_player.call_on_player_move()
        return True, False

    def add_gold(self, gold: int):
        self.gold += gold
        self.game.main_widget.right_pannel.update_gold_text()

    def set_dead(self, dead: bool):
        self.dead = dead
        self.game.end_game("You disembarked over the ocean!")
        for player in self.get_enabled_players():
            player.enabled = dead

    def remove_gold(self, gold: int):
        self.gold -= gold
        self.game.main_widget.right_pannel.update_gold_text()
        if self.gold < 0:
            self.game.end_game("Your gold fell below 0!")


P = TypeVar("P", bound=PlayerEntity)
