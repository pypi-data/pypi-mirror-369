from __future__ import annotations

import random

from tpg import entities, game, squares, popup
from PySide6 import QtGui


class Tribe(entities.entity.Entity):
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
            valid_squares=[squares.Land],  # tribe can only move on land
            invalid_squares=[
                Tribe,
                entities.chest.Chest,
            ],  # tribe can't spawn on top of other tribes or chests
            player_interact_radius=0,  # tribe can only interact with player if on top of it
        )

        self.investment = None
        self.has_invested = False
        self.just_rejected = False
        self.investment_start_turn = None

        self.brush = QtGui.QBrush(QtGui.QColor(200, 128, 20))  # brown

    def invest(self, amount: int):
        if not self.can_invest():
            return False
        self.investment = amount
        self.has_invested = True
        self.investment_start_turn = self.game.turn_counter
        return True

    def turns_since(self) -> int | None:
        """Get the number of turns since the tribe invested in the player.

        Returns:
            int | None: The number of turns since the tribe invested in the player.
        """
        if self.investment_start_turn is None:
            return None
        return self.game.turn_counter - self.investment_start_turn

    def on_eat(self, cannibal: entities.cannibal.Cannibal):
        self.investment = None
        self.enabled = False

    def can_invest(self):
        return (
            self.investment is None
            and not self.has_invested
            and not self.just_rejected
            and self.investment_start_turn is None
        )

    def give_investment(self, amount: float):
        if self.investment is None:
            return
        to_give = int(self.investment * amount)
        self.game.add_log_text(f"A tribe at {self.pos} gave you {to_give}G!")
        self.game.entities.popup.add_text(f"+{to_give}G", popup.Icon.TRIBE, self)
        self.game.entities.player.add_gold(to_give)

    def remove_investment(self):
        self.investment = None
        self.game.add_log_text(f"A tribe's silver mine at {self.pos} has run out")
        self.game.entities.popup.add_text("RAN OUT", popup.Icon.TRIBE, self)

    def do_payment(self):
        if self.investment is None or not self.enabled:
            return

        num = random.randint(1, self.game.investment_max_number)  # 1-50
        for min, max, amount in self.game.invest_types:
            if num not in range(min, max + 1):
                continue

            if amount is None:
                self.remove_investment()
            else:
                self.give_investment(amount)

    def engage_in_trade(self, player: entities.player.PlayerEntity):
        self.game.entities.ask_to_trade(self, player)

    def do_turn(self, was_p_move_valid: bool):
        if self.investment is None or not was_p_move_valid:
            return
        turns_since = self.turns_since()
        if turns_since is None:
            return
        if (
            turns_since % self.game.investment_interval == 0 and turns_since != 0
        ):  # check if the number of turns since the tribe invested in the player is a multiple of the investment interval
            self.do_payment()

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        res = super().on_player_move(player)
        if not res:
            return False
        if (
            self.just_rejected
        ):  # don't engage in trade if the player just rejected the tribe
            self.just_rejected = False

        if self.can_invest():
            self.engage_in_trade(player)

        return True
