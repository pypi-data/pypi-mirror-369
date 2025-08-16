from __future__ import annotations

import random
from tpg import entities, game, squares, popup

from PySide6 import QtGui

from tpg.entities.player import PlayerEntity


class Trader(entities.entity.Entity):
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
            valid_squares=[squares.Ocean],  # trader can only move on ocean
            invalid_squares=[
                entities.sea_monster.SeaMonster,  # trader can't move on top of sea monster
                entities.pirate.Pirate,  # trader can't move on top of pirates
                Trader,  # trader can't move on top of other traders
            ],
            player_interact_radius=1,  # trader can only interact with player if adjacent
        )

        self.visible = self.game.trader_visible

        self.hide_counter = 0
        self.interact_counter = self.game.trader_hidden_duration
        self.can_appear = False

        self.brush = QtGui.QBrush(QtGui.QColor(100, 20, 100))  # purple

    @property
    def speed(self) -> int:
        return 2

    def do_turn(self, was_p_move_valid: bool):
        self.interact_counter += 1  # increment interact counter

        if self.game.trader_visible:
            self.visible = True
        elif self.visible:  # only visible for one turn
            self.visible = False

        if not self.visible:
            self.hide_counter += 1  # increment hide counter
            if (
                self.hide_counter >= self.game.trader_hidden_duration
            ):  # if trader has been hidden for too long
                self.can_appear = True  # trader can appear again

        directions = squares.directions
        direction = random.choice(directions)

        self.move(direction)  # move in a random direction

        if not self.visible and self.can_appear:
            roll = random.randint(1, 100)
            if roll > self.game.trader_spot_probability:  # roll for trader to appear
                return

            self.visible = True
            self.hide_counter = 0
            self.can_appear = False

    def on_player_move(self, player: PlayerEntity) -> bool:
        res = super().on_player_move(player)
        if not res:
            return False
        if (
            self.interact_counter < self.game.trader_hidden_duration
        ):  # delay after first interaction
            return False

        self.interact_counter = 0

        self.game.entities.ask_trader_q(self, player)

        return True

    def fight(self, player: entities.player.PlayerEntity):
        if not self.enabled:
            return
        self.enabled = False
        self.visible = False
        roll = random.randint(1, 100)
        if roll <= self.game.capture_cargo_prop:  # 80/100
            cargo_plunder = random.randint(self.game.cargo_min, self.game.cargo_max)
            self.game.entities.player.add_gold(cargo_plunder)
            self.game.entities.popup.add_text(
                f"PLUNDERED +{cargo_plunder}G",
                popup.Icon.TRADER,
                self,
            )
            self.game.add_log_text(f"You plundered a trader and stole {cargo_plunder}G")

            return

        roll -= self.game.capture_cargo_prop

        if roll <= self.game.trader_sink_prob:  # 20/100 * 10/20 = 0.1
            self.game.entities.popup.add_text(
                f"SUNK",
                popup.Icon.TRADER,
                self,
            )
            self.game.add_log_text(f"The trader along with the cargo sunk")

            return

        roll -= self.game.trader_sink_prob

        if roll <= self.game.trader_fight_back_prob:  # 0.1 * 5/10 = 0.05
            damage = random.randint(
                self.game.repair_cost_min, self.game.repair_cost_max
            )
            self.game.entities.player.remove_gold(damage)
            self.game.entities.popup.add_text(
                f"REPAIRS -{damage}G",
                popup.Icon.TRADER,
                self,
            )
            self.game.add_log_text(
                f"The trader fought back and damaged your ship costing {damage}G"
            )
            return

        roll -= self.game.trader_fight_back_prob

        if roll <= self.game.trader_armed_prob:  # 0.05 * 5/5 = 0.05
            self.game.entities.player_sunk()
            self.game.entities.popup.add_text(
                f"HEAVILY ARMED",
                popup.Icon.TRADER,
                self,
            )
            self.game.add_log_text(
                f"The trader was actually heavily armed and you were killed"
            )
            return
