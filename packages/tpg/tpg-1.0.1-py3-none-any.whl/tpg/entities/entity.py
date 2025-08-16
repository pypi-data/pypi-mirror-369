from __future__ import annotations
import math
import random
from typing import Callable, Generator, TypeVar
import uuid

from tpg import entities, game, squares, popup, upgrade

from PySide6 import QtGui


class Entity(squares.Square):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        enabled: bool = True,
        valid_squares: list[type[squares.Square]] | None = None,
        invalid_squares: list[type[squares.Square]] | None = None,
        player_interact_radius: int | None = None,
    ):
        """Entity class

        Args:
            game (game.Game): Game instance
            x (int): X position
            y (int): Y position
            enabled (bool, optional): Whether the entity is enabled. Defaults to True. If False, the entity will not be interactable.
            valid_squares (list[type[squares.Square]] | None, optional): The squares the entity can move/be spawned on. Defaults to None.
            invalid_squares (list[type[squares.Square]] | None, optional): The squares the entity can't move/be spawned on. Defaults to None.
            player_interact_radius (int | None, optional): The radius the player can interact with the entity. Defaults to None. If -1, the player can interact with the entity from any distance.
        """
        super().__init__(game, x, y)

        self.id = str(uuid.uuid4())  # unique id

        self.enabled = enabled

        self.can_move_on = valid_squares
        self.cant_move_on = invalid_squares

        self.player_interact_radius = player_interact_radius

        if x == -1 or y == -1:  # if x or y is -1, generate random position
            pos = self.generate_random_pos(True)
            self.x = pos[0]
            self.y = pos[1]

        self.brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))  # black

    def generate_random_pos(self, is_init: bool) -> tuple[int, int]:
        all = self.game.terrain.all_positions_s.copy()  # get all positions

        if (
            len(all) > 10_000
        ):  # optimization as doing list(all) and then random.choice can get quite slow as board gets larger
            while True:
                pos_x = random.randint(0, self.game.terrain.width - 1)
                pos_y = random.randint(0, self.game.terrain.height - 1)
                sq = self.game.terrain[pos_x][pos_y]
                if self.valid_square(sq, is_init):
                    return (pos_x, pos_y)

        while all:  # while there are still positions
            pos = random.choice(list(all))  # choose a random position
            sq = self.game.terrain[pos[0]][pos[1]]
            if self.valid_square(sq, is_init):  # if the square is valid,
                return pos
            all.remove(pos)  # remove the position from the list

        raise ValueError("No valid spaces found!")

    @property
    def speed(self) -> int:
        return 0

    def do_turn(self, was_p_move_valid: bool):
        """Put logic for the entity's turn here

        Args:
            was_p_move_valid (bool): Whether the player's move was valid. Used in investment logic.
        """

    def move(self, direction: tuple[int, int]) -> bool:
        """Move the entity in a direction

        Args:
            direction (tuple[int, int]): (dx, dy)

        Returns:
            bool: Whether the entity moved
        """
        has_moved: bool = False
        for _ in range(self.speed):  # move the entity based on its speed
            if not self.move_one(direction):  # if the entity can't move, return
                return has_moved
            has_moved = True
        return has_moved

    def move_one(self, direction: tuple[int, int]) -> bool:
        """Move the entity one step in a direction

        Args:
            direction (tuple[int, int]): (dx, dy)

        Returns:
            bool: Whether the entity moved
        """
        if not self.enabled:  # if the entity is not enabled, don't move
            return False
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]

        args = ((new_x, new_y), (self.x, self.y), direction)

        if new_x < 0 or new_y < 0:  # if the new position is out of bounds, return
            return False

        if (
            new_x >= self.game.terrain.width or new_y >= self.game.terrain.height
        ):  # if the new position is out of bounds, return
            return False

        if not self.valid_move(*args):  # if the move is not valid, return
            return False

        self.x = new_x
        self.y = new_y

        self.on_move_one_success(*args)  # call on_move_one_success

        return True

    def valid_square(
        self,
        square: squares.Square,
        is_init: bool,
        ignore_entities: bool = False,
    ) -> bool:
        """Check if a square is valid for the entity to move to

        Args:
            square (squares.Square): The square to check
            is_init (bool): Whether the entity is being initialized
            ignore_entities (bool, optional): Whether to ignore entities. Defaults to False.

        Returns:
            bool: Whether the square is valid
        """
        if self.cant_move_on is not None:  # if the entity can't move on certain squares
            for t in self.cant_move_on:  # iterate over the squares
                if isinstance(
                    square, t
                ):  # if the square to check is an instance of the square type
                    return False
                if (
                    issubclass(t, Entity) and not ignore_entities
                ):  # if the square is an entity
                    entities = self.game.entities.get_enabled_square_t(
                        square, t
                    )  # get the entities on the square of the type
                    if next(entities, None):  # if there are any entities
                        return False

        if self.can_move_on is not None:  # if the entity can move on certain squares
            for t in self.can_move_on:  # iterate over the squares
                if isinstance(
                    square, t
                ):  # if the square to check is an instance of the square type
                    return True
                if (
                    isinstance(t, Entity) and not ignore_entities
                ):  # if the square is an entity
                    entities = self.game.entities.get_enabled_square_t(
                        square, t
                    )  # get the entities on the square of the type
                    if next(entities, None):  # if there are any entities
                        return True

        if self.can_move_on is not None:  # if the entity can move on certain squares
            return False

        return True

    def valid_move(
        self,
        new: tuple[int, int],
        old: tuple[int, int],
        direction: tuple[int, int],
    ) -> bool:
        """Check if a move is valid

        Args:
            new (tuple[int, int]): The new position
            old (tuple[int, int]): The old position
            direction (tuple[int, int]): The direction

        Returns:
            bool: Whether the move is valid
        """
        square = self.game.terrain[new[0]][new[1]]

        return self.valid_square(square, False)

    def on_move_one_success(
        self, new: tuple[int, int], old: tuple[int, int], direction: tuple[int, int]
    ):
        """Called when the entity successfully moves one step

        Args:
            new (tuple[int, int]): The new position
            old (tuple[int, int]): The old position
            direction (tuple[int, int]): The direction
        """

    def on_player_move(self, player: entities.player.PlayerEntity) -> bool:
        """Called when the player moves one step

        Args:
            player (entities.player.PlayerEntity): The player

        Returns:
            bool: Whether the player is in the entity's radius
        """
        if self.player_interact_radius is None:  # if the player interact radius is None
            return False
        if (
            self.is_adjacent_to(
                player, radius=self.player_interact_radius
            )  # if the player is in the entity's radius
            or self.player_interact_radius == -1  # or the player interact radius is -1
        ):
            return True
        return False


E = TypeVar("E", bound=Entity)  # generic type for Entity


class Entities:
    def __init__(
        self,
        game: game.Game,
    ):
        """Entities class

        Args:
            game (game.Game): Game instance
        """
        self.game = game

    def create(
        self,
        pirate_range: list[int],
        total_chests: int,
        gold_range: list[int],
        ransom_range: list[int],
        total_cannibals: int,
        total_sea_monsters: int,
        total_tribes: int,
        total_traders: int,
        near_range: int,
        lookout_range: int,
    ):
        """Create entities

        Args:
            pirate_range (list[int]): The range of possible pirate counts
            total_chests (int): The total number of chests
            gold_range (list[int]): The range of possible gold values a chest can have
            ransom_range (list[int]): The range of possible ransom values a pirate can have
            total_cannibals (int): The total number of cannibals
            total_sea_monsters (int): The total number of sea monsters
            total_tribes (int): The total number of tribes
            total_traders (int): The total number of traders
            near_range (int): The range of squares a player can see nearby on the lookout
            lookout_range (int): The range of squares a player can see on the lookout
        """
        self._entities: list[Entity] = []

        self.pirate_lookout: list[squares.PirateCount] = []

        self.rumours: list[squares.SeaMonsterRumour] = []

        self.popup = popup.PopUp(self.game)

        self.pirate_range = pirate_range
        self.total_chests = total_chests
        self.gold_range = gold_range
        self.ransom_range = ransom_range
        self.total_cannibals = total_cannibals
        self.near_range = near_range
        self.lookout_range = lookout_range

        self.create_player()
        self.create_pirates(pirate_range, ransom_range)
        self.create_traders(total_traders)

        self.create_cannibals(total_cannibals)
        self.create_sea_monsters(total_sea_monsters)

        self.create_chests(total_chests, gold_range)
        self.create_friendly_tribes(total_tribes)

        self.update_pirate_count()

    def create_player(self):
        self.player = entities.player.Player(self.game)
        self.player.add_player(
            entities.player.BoatPlayer(self.game, 0, 0)
        )  # add boat player at (0, 0)
        self.player.add_player(
            entities.player.LandPlayer(self.game, 0, 0, False)
        )  # add land player at (0, 0) and set it to not enabled

    def create_friendly_tribes(self, total: int):
        for _ in range(total):
            tribe = self.create_tribe()
            self.add(tribe)

    def create_tribe(self):
        return entities.tribe.Tribe(
            self.game, -1, -1
        )  # create tribe at random position

    def create_pirates(self, pirate_range: list[int], ransom_range: list[int]):
        total_pirates = random.choice(pirate_range)

        slower_pirates = total_pirates // 2
        faster_pirates = total_pirates - slower_pirates

        for i in range(total_pirates):
            pirate = self.create_pirate(ransom_range, i >= faster_pirates)
            self.add(pirate)

        self.update_pirate_count()

    def create_traders(self, total_traders: int):
        for _ in range(total_traders):
            trader = self.create_trader()
            self.add(trader)

    def create_cannibals(self, total_cannibals: int):
        for _ in range(total_cannibals):
            cannibal = self.create_cannibal()
            self.add(cannibal)

    def create_sea_monsters(self, total_sea_monster: int):
        for _ in range(total_sea_monster):
            sea_monster = self.create_sea_monster()
            self.add(sea_monster)

    def create_cannibal(self):
        cannibal = entities.cannibal.Cannibal(
            self.game, -1, -1
        )  # create cannibal at random position
        return cannibal

    def create_sea_monster(self):
        return entities.sea_monster.SeaMonster(
            self.game, -1, -1
        )  # create sea monster at random position

    def create_trader(self):
        return entities.trader.Trader(
            self.game, -1, -1
        )  # create trader at random position

    def update_pirate_count(self):
        if (
            not self.has_pirate_lookout()
        ):  # if the player doesn't have the improved lookout upgrade,
            return
        self.pirate_lookout = []

        boat_player = self.player.get_boat_player()  # get the boat player
        if boat_player is None:
            return

        summary_info: dict[str, str] = {}

        directions = [
            ("west", -1, 0),
            ("east", 1, 0),
            ("north", 0, -1),
            ("south", 0, 1),
        ]
        for dir in directions:
            is_close = False
            include_equals = dir[1:] in [
                (0, -1),
                (0, 1),
            ]  # which directions include the diagonal squares
            total_pirate_counts = 0
            near_pirate_count = 0
            near_trader_count = 0
            for pirate in self.get_enabled_npcs_t(
                entities.pirate.Pirate
            ):  # iterate over pirates
                if pirate.is_adjacent_to(  # if the pirate is adjacent to the boat player within the larger range
                    boat_player,
                    radius=self.lookout_range,
                    direction=dir[1:],
                    include_equals=include_equals,
                ):
                    total_pirate_counts += 1  # increment the total pirate count

                if pirate.is_adjacent_to(  # if the pirate is adjacent to the boat player within the smaller range
                    boat_player,
                    radius=self.near_range,
                    direction=dir[1:],
                    include_equals=include_equals,
                ):
                    is_close = True
                    near_pirate_count += 1  # increment the near pirate count

            for trader in self.get_enabled_npcs_t(
                entities.trader.Trader
            ):  # iterate over traders
                if trader.is_adjacent_to(  # if the trader is adjacent to the boat player within the smaller range
                    boat_player,
                    radius=self.near_range,
                    direction=dir[1:],
                    include_equals=include_equals,
                ):
                    is_close = True
                    near_trader_count += 1  # increment the near trader count

            # create the summary info text for lookout info box
            text = ""
            if total_pirate_counts - near_pirate_count != 0:
                text += (
                    f"{total_pirate_counts-near_pirate_count} pirates to the {dir[0]}"
                )
                if near_pirate_count != 0:
                    text += f", {near_pirate_count} pirates nearby"
            elif near_pirate_count != 0:
                text += f"{near_pirate_count} pirates nearby to the {dir[0]}"

            if near_trader_count != 0:
                text += f"{near_trader_count} traders nearby to the {dir[0]}"

            text = text.strip()

            summary_info[dir[0]] = text  # add the text to the summary info

            for (
                sq
            ) in boat_player.get_adjacent_t(  # iterate over the ocean squares adjacent to the boat player
                squares.Ocean,
                radius=self.lookout_range,
                direction=dir[1:],
                include_self=False,
                include_equals=include_equals,
            ):
                if is_close:  # if the pirate is close to the boat player
                    is_close_sq = boat_player.is_adjacent_to(
                        sq, radius=self.near_range
                    )  # check if the square is close
                else:
                    is_close_sq = False

                if is_close_sq:
                    pirate_count = near_pirate_count
                    trader_count = near_trader_count
                else:
                    pirate_count = total_pirate_counts - near_pirate_count
                    trader_count = 0

                sq = squares.PirateCount(
                    self.game,
                    sq.x,
                    sq.y,
                    pirate_count,
                    trader_count,
                    dir[1:],
                    is_close_sq,
                )
                self.pirate_lookout.append(sq)

        self.game.clear_lookout_text()
        self.game.add_lookout_text("IMPROVED LOOKOUT")
        self.game.add_lookout_text("------------------------")
        added = False
        for text in summary_info.values():
            if text:
                self.game.add_lookout_text(text)
                added = True
        if not added:
            self.game.add_lookout_text("all clear")
        self.game.add_lookout_text("------------------------")

    def has_pirate_lookout(self) -> bool:
        return self.player.has_upgrade(upgrade.UpgradeType.IMPROVED_LOOKOUT)

    def create_pirate(self, ransom_range: list[int], move_faster_than_player: bool):
        ransom = random.choice(ransom_range) / 100  # choose a random ransom value
        pirate = entities.pirate.Pirate(
            self.game, -1, -1, move_faster_than_player, ransom
        )  # create pirate at random position
        return pirate

    def create_chests(self, total: int, gold_range: list[int]):
        total = min(
            total, len(self.game.terrain.land_spaces)
        )  # get the total number of chests
        for _ in range(total):
            chest = self.create_chest(gold_range)
            self.add(chest)

    def create_chest(self, gold_range: list[int]):
        gold = random.choice(gold_range)
        return entities.chest.Chest(
            self.game, -1, -1, gold
        )  # create chest at random position with random gold value

    def add(self, *entity: Entity):
        self._entities.extend(entity)

    def remove(self, entity: Entity) -> bool:
        """Remove an entity

        Args:
            entity (Entity): The entity to remove

        Returns:
            bool: Whether the entity was removed
        """
        entity.enabled = False
        for e2 in self._entities.copy():
            if e2.id == entity.id:
                self._entities.remove(e2)
                return True
        return False

    @property
    def entities(self):
        return self._entities + self.player.flattened

    def get_enabled_npcs(self) -> Generator[Entity, None, None]:
        for entity in self._entities:
            if entity.enabled:
                yield entity

    def get_enabled_square_t(
        self, square: squares.Square, t: type[E]
    ) -> Generator[E, None, None]:
        """Get enabled entities of a certain type on a square

        Args:
            square (squares.Square): The square to check
            t (type[E]): The type of entity

        Yields:
            Generator[E, None, None]: The entities
        """
        for entity in self._entities:
            if (
                entity.x == square.x
                and entity.y == square.y
                and entity.enabled
                and isinstance(entity, t)
            ):
                yield entity

    def get_enabled_npcs_t(self, t: type[E]) -> Generator[E, None, None]:
        """Get enabled entities of a certain type

        Args:
            t (type[E]): The type of entity

        Yields:
            Generator[E, None, None]: The entities
        """
        for entity in self._entities:
            if entity.enabled and isinstance(entity, t):
                yield entity

    def __iter__(self):
        return iter(self.entities)

    def move_player(self, direction: tuple[int, int]):
        if (
            self.game.game_over or self.game.lock_movement
        ):  # if the game is over or movement is locked,
            return False
        players = self.player.get_enabled_players()
        p_move_valid: bool = False
        for player in players:  # iterate over enabled players
            if player.move(direction):
                p_move_valid = True

        return p_move_valid  # return whether the player actually moved

    def done_p_move(self, was_valid: bool):
        if self.game.game_over:  # if the game is over, return
            return False
        if self.game.lock_movement:  # if movement is locked, return
            return False

        self.calculate_pirate_move_speed()  # shuffle pirate move speed

        for entity in self.get_enabled_npcs():  # iterate over enabled entities
            entity.do_turn(was_valid)  # do the entity's turn

        self.create_rumours()  # create sea monster rumours

        self.update_pirate_count()  # update pirate count for improved lookout

        self.update_pirate_chests()  # update pirate chests, e.g hiding and finding chests

        self.game.main_widget.right_pannel.upgrade_screen.update_table()  # update upgrade screen
        self.game.main_widget.bottom_pannel.lookout_log.setHidden(  # hide lookout log if player does not have improved lookout
            not self.has_pirate_lookout()
        )

        self.game.turn_counter += 1  # increment turn counter

        self.add_ship_log()  # add ship log entry

    def add_ship_log(self):
        turn_text = f"TURN {self.game.turn_counter + 1}"  # create turn text

        font = QtGui.QFont()
        font.setPixelSize(10)
        self.game.main_widget.right_pannel.ship_log.text_area.setFont(font)  # set font

        dash_size = QtGui.QFontMetrics(font).horizontalAdvance("-")  # get dash size

        text_area_width = (
            self.game.main_widget.right_pannel.ship_log.text_area.width()
        )  # get text area width

        dash_len = (
            text_area_width // dash_size
        ) // 2  # calculate dash length so it fits the text area

        self.game.add_log_text("-" * dash_len)
        self.game.add_log_text(turn_text)
        self.game.add_log_text("-" * dash_len)

    def update_pirate_chests(self):
        self.hide_chest()
        self.find_chest()

    def find_chest(self):
        if (
            self.game.turn_counter % self.game.pirate_find_chest_interval != 0
        ):  # only find chests every n turns (5 by default)
            return
        roll = random.randint(1, 100)

        if roll > self.game.pirate_find_chest_chance:  # roll for finding chest
            return

        chests = list(self.get_enabled_npcs_t(entities.chest.Chest))  # get chests
        if not chests:
            return

        chest = random.choice(chests)
        self.remove(chest)  # remove random chest

    def hide_chest(self):
        if (
            self.game.turn_counter % self.game.pirate_hide_chest_interval != 0
        ):  # only hide chests every n turns (5 by default)
            return
        roll = random.randint(1, 100)

        if roll > self.game.pirate_hide_chest_chance:  # roll for hiding chest
            return
        if (
            len(list(self.get_enabled_npcs_t(entities.chest.Chest)))
            < self.game.total_hidden_chests  # only hide chests if there are less than the total hidden chests allowed
        ):
            new_chest = self.create_chest(self.gold_range)  # create new chest
            self.add(new_chest)

    def create_rumours(self):
        if (
            self.game.turn_counter % self.game.rumour_interval != 0
        ):  # only create rumours every n turns (5 by default)
            return

        roll = random.randint(1, 100)

        if roll > self.game.rumour_probability:  # roll for creating rumour
            return

        self.rumours = []

        for sea_monster in self.get_enabled_npcs_t(
            entities.sea_monster.SeaMonster
        ):  # iterate over sea monsters
            rumour = (
                sea_monster.give_rumour()
            )  # get rumour (+- 5 ocean squares from sea monster)
            if rumour is None:
                continue
            rumour_obj = squares.SeaMonsterRumour(
                self.game, rumour[0], rumour[1]
            )  # create rumour
            self.rumours.append(rumour_obj)

    def calculate_pirate_move_speed(self):
        pirates = list(self.get_enabled_npcs_t(entities.pirate.Pirate))
        random.shuffle(pirates)

        move_fast_count = (
            len(pirates) // 2
        )  # move half of the pirates faster than the player

        for pirate in pirates:
            pirate.move_faster_than_player = (
                move_fast_count >= 0
            )  # set move faster than player
            move_fast_count -= 1

    def disembark(self) -> tuple[bool, bool]:
        return self.player.set_on_land(True)

    def embark(self) -> bool:
        return self.player.set_on_land(False)[0]

    def toggle_on_land(self):
        if self.game.lock_movement:  # if movement is locked, return
            return False
        allowed, dead = self.disembark()
        if allowed:
            return True
        if dead:  # if the player disembarked over the ocean
            self.player.set_dead(True)
            return False

        if self.embark():
            return True
        else:
            self.game.add_log_text("You have to be adjacent to your boat to embark")
        return False

    def loot_chest(
        self, chest: entities.chest.Chest, player: entities.player.PlayerEntity
    ):
        gold = chest.gold
        self.player.add_gold(gold)  # add gold to player

        self.game.add_log_text(f"You looted a chest and gained {gold}G")

        self.popup.add_text(f"+{gold}G", popup.Icon.CHEST, chest)

        self.remove(chest)  # remove chest

    def plunder_booty(
        self, pirate: entities.pirate.Pirate, player: entities.player.PlayerEntity
    ):
        ransom = pirate.ransom

        if self.player.has_upgrade(upgrade.UpgradeType.BETTER_DEFENCES):
            ransom *= (
                0.5  # if the player has the better defences upgrade, ransom is halved
            )

        curr_gold = self.player.gold
        takeage = curr_gold * ransom
        takeage = math.floor(takeage)  # round down

        self.player.remove_gold(takeage)  # remove gold from player

        if takeage != 0:
            self.popup.add_text(f"-{takeage}G", popup.Icon.PIRATE, pirate)
            self.game.add_log_text(
                f"Your booty was plundered by a pirate. You lost {takeage}G!"
            )

        faster_than_player = pirate.move_faster_than_player

        self.remove(pirate)

        new_pirate = self.create_pirate(
            self.ransom_range, faster_than_player
        )  # create new pirate

        self.add(new_pirate)

    def eat_player(
        self,
        entity: entities.cannibal.Cannibal | entities.sea_monster.SeaMonster,
        player: entities.player.PlayerEntity,
    ):
        if (
            not self.game.can_be_eaten or not player.can_be_eated
        ):  # if the player can't be eaten
            return
        if isinstance(
            entity, entities.cannibal.Cannibal
        ):  # if the entity is a cannibal
            self.game.end_game("You were eaten by a cannibal")
        else:  # if the entity is a sea monster
            self.game.end_game("You were eaten by a sea monster")

    def player_sunk(self):
        self.game.end_game("The trader was heavily armed and you died")

    def ask_to_trade(
        self, tribe: entities.tribe.Tribe, player: entities.player.PlayerEntity
    ):
        self.update_pirate_count()  # update pirate count for improved lookout

        start_investment: Callable[[int], None] = lambda amount: self.start_investment(
            amount, tribe
        )  # start investment function
        self.game.main_widget.bottom_pannel.trade_popup.investSubmitted.connect(
            start_investment
        )  # connect signals
        self.game.main_widget.bottom_pannel.trade_popup.investCancelled.connect(
            lambda: self.cancel_investment(tribe)
        )  # connect signals
        self.game.lock_movement = True  # lock player movement
        self.game.main_widget.bottom_pannel.trade_popup.start_investment()

    def eat_tribe(
        self, cannibal: entities.cannibal.Cannibal, tribe: entities.tribe.Tribe
    ):
        tribe.on_eat(cannibal)
        self.remove(tribe)

    def start_investment(self, amount: int, tribe: entities.tribe.Tribe):
        self.game.lock_movement = False
        tribe.invest(amount)
        self.game.main_widget.bottom_pannel.trade_popup.disconnect_signals()

    def cancel_investment(self, tribe: entities.tribe.Tribe):
        self.game.lock_movement = False
        tribe.just_rejected = True
        self.game.main_widget.bottom_pannel.trade_popup.disconnect_signals()

    def ask_trader_q(
        self, trader: entities.trader.Trader, player: entities.player.PlayerEntity
    ):
        self.update_pirate_count()  # update pirate count for improved lookout

        self.game.lock_movement = True

        self.game.main_widget.bottom_pannel.trader_popup.fightIgnored.connect(
            self.fight_ignored  # connect signals
        )
        self.game.main_widget.bottom_pannel.trader_popup.fightSubmitted.connect(
            lambda: self.fight_submitted(trader, player)
        )  # connect signals

        self.game.main_widget.bottom_pannel.trader_popup.start_choice(trader)

    def fight_ignored(self):
        self.game.lock_movement = False
        self.game.main_widget.bottom_pannel.trader_popup.disconnect_signals()

    def fight_submitted(
        self, trader: entities.trader.Trader, player: entities.player.PlayerEntity
    ):
        self.game.lock_movement = False
        trader.fight(player)
        self.game.main_widget.bottom_pannel.trader_popup.disconnect_signals()
