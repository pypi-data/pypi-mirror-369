from __future__ import annotations

from tpg import entities, game, squares

from PySide6 import QtGui


class Chest(entities.entity.Entity):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        gold: int,
    ):
        super().__init__(
            game,
            x,
            y,
            player_interact_radius=0,  # player can interact with chest only if on top of it
            valid_squares=[squares.Land],  # chest can only be on land
            invalid_squares=[
                Chest,
                entities.tribe.Tribe,
            ],  # chest can't be on top of other chests or tribes
        )

        self.gold = gold
        self.brush = QtGui.QBrush(QtGui.QColor(255, 255, 0))  # yellow

        self.visible = self.game.chest_visible

    def loot(self, player: entities.player.PlayerEntity):
        self.game.entities.loot_chest(self, player)

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        res = super().on_player_move(player)
        if not res:
            return False

        self.loot(player)  # loot the chest if player is on top of it
        return True
