from __future__ import annotations

import os
import time

from PySide6.QtCore import Qt

from tpg import entities, terrain, ui, upgrade, renderer


class Game:
    def __init__(self):
        self.screen_size: tuple[int, int] = (
            700,
            500,
        )  # width, height of the screen in pixels

        self.__debug = False  # debug mode
        self.update_debug()

        self.__fps = 60
        self.frame = 0  # frame counter
        self.turn_counter = 0  # turn counter
        self.held_keys: set[int] = set()  # keys currently being held

        self.previous_frame = 0
        self.current_frame = 0

        self.island_layout: list[tuple[tuple[int, int], int]] = [
            ((10, 10), 3),  # ((width, height), number of islands)
            ((8, 8), 2),
            ((6, 6), 1),
            ((4, 4), 2),
        ]

        self.keep_island_on_screen_factor = 0.5  # don't let islands spawn more than 50% offscreen, 1 = 100% on screen, 0 = only ensure 1 square is on screen

        self.grid_size: tuple[int, int] = (
            70,
            50,
        )  # width, height of the grid in squares
        self.safe_square = (2, 2)  # (x, y) of the safe region for generating islands

        self.pirate_min = 10  # min number of pirates
        self.pirate_max = 20  # max number of pirates
        self.pirate_hide_chest_interval = 5  # how often pirates hide chests
        self.pirate_find_chest_interval = 5  # how often pirates find chests
        self.pirate_hide_chest_chance = 20  # chance of pirates hiding chests
        self.pirate_find_chest_chance = 5  # chance of pirates finding chests

        self.edge_square_probability = 33  # probability of edge square existing
        self.inside_square_probability = 95  # probability of inside square existing

        self.total_chests_start = 10  # total number of chests at start
        self.total_hidden_chests = 15  # total number of hidden chests

        self.trader_spot_probability = 5  # probability of trader being spotted
        self.trader_hidden_duration = 5  # how long trader is hidden for

        self.gold_min = 250  # min gold in chest
        self.gold_max = 750  # max gold in chest

        self.ransom_min = 15  # min ransom %
        self.ransom_max = 65  # max ransom %

        self.total_cannibals = 3  # total number of cannibals
        self.total_sea_monsters = 2  # total number of sea monsters
        self.total_tribes = 3  # total number of tribes
        self.total_traders = 5  # total number of traders

        self.rumour_interval = 5  # how often to give a sea monster rumour
        self.rumour_probability = 50  # probability of giving a sea monster rumour

        self.lookout_near_range = 2  # lookout near range
        self.lookout_far_range = 5  # lookout far range

        self.capture_cargo_prop = 80  # probability of player capturing trader cargo

        self.cargo_min = 200  # min trader cargo
        self.cargo_max = 600  # max trader cargo

        self.trader_sink_prob = 10  # probability of trader sinking
        self.trader_fight_back_prob = 5  # probability of trader fighting back
        self.trader_armed_prob = 5  # probability of trader being heavily armed

        self.repair_cost_min = 100  # min repair cost if trader fights back
        self.repair_cost_max = 200  # max repair cost if trader fights back

        self.min_invest = 100  # min investment for tribe
        self.max_invest = 1000  # max investment for tribe
        self.investment_interval = 5  # how often tribe gives investment
        self.investment_max_number = 50  # max number for trader type investment
        self.invest_types: list[tuple[int, int, float | None]] = [
            (1, 1, None),  # 1-1 end investment
            (2, 10, 0),  # 2-10 Zero
            (11, 20, 0.05),  # 11-20 0.05x investment
            (21, 30, 0.07),  # 21-30 0.07x investment
            (31, 40, 0.09),  # 31-40 0.09x investment
            (41, 50, 0.15),  # 41-50 0.15x investment
        ]

        self.upgrades: list[upgrade.Upgrade] = [
            upgrade.Upgrade(
                upgrade.UpgradeType.BIGGER_SAIL,  # type
                "Bigger Sail",  # name
                1000,  # cost
                "Increases boat speed by 1",  # description
            ),
            upgrade.Upgrade(
                upgrade.UpgradeType.BETTER_DEFENCES,
                "Better Defences",
                1000,
                "Reduces ransom by 50%",
            ),
            upgrade.Upgrade(
                upgrade.UpgradeType.MAP_READING,
                "Map Reading",
                1000,
                "Increases land speed by 1",
            ),
            upgrade.Upgrade(
                upgrade.UpgradeType.IMPROVED_LOOKOUT,
                "Improved Lookout",
                1500,
                "Improves ability to see pirates",
            ),
        ]

        self.__painter = None
        self.__main_widget = None

        self.create_game()

    def add_log_text(self, text: str):
        self.main_widget.right_pannel.ship_log.add_text(text)

    def add_lookout_text(self, text: str):
        self.main_widget.bottom_pannel.lookout_log.add_text(text)

    def clear_lookout_text(self):
        self.main_widget.bottom_pannel.lookout_log.clear_text()

    def create_game(self):
        self.game_over = False
        self.lock_movement = False

        self.frame = 0
        self.turn_counter = 0

        self.terrain = terrain.Terrain(
            self,
            grid_size=self.grid_size,
            islands=self.island_layout,
            safe_square=self.safe_square,
        )
        self.terrain.create()

        self.entities = entities.entity.Entities(
            self,
        )
        self.entities.create(
            pirate_range=list(range(self.pirate_min, self.pirate_max)),
            total_chests=self.total_chests_start,
            gold_range=list(range(self.gold_min, self.gold_max)),
            ransom_range=list(range(self.ransom_min, self.ransom_max)),
            total_cannibals=self.total_cannibals,
            total_sea_monsters=self.total_sea_monsters,
            total_tribes=self.total_tribes,
            total_traders=self.total_traders,
            near_range=self.lookout_near_range,
            lookout_range=self.lookout_far_range,
        )

        if self.__main_widget is not None:
            self.main_widget.right_pannel.update_gold_text()
            self.main_widget.right_pannel.update_embark_text()
            self.main_widget.right_pannel.upgrade_screen.reset()

            self.entities.add_ship_log()

    @property
    def fps(self) -> int:
        return self.__fps

    @fps.setter
    def fps(self, value: int):
        self.__fps = value
        self.main_widget.update_fps()

    @property
    def debug(self) -> bool:
        return self.__debug

    @debug.setter
    def debug(self, value: bool):
        self.__debug = value
        self.update_debug()

    def update_debug(self):
        self.pirate_visible = self.debug
        self.chest_visible = self.debug
        self.cannibal_visible = self.debug
        self.sea_monster_visible = self.debug
        self.trader_visible = self.debug

        self.can_be_eaten = not self.debug

    def get_asset(self, asset_name: str):
        return os.path.join(os.path.dirname(__file__), "files", "assets", asset_name)

    @property
    def painter(self) -> renderer.GraphicsScreen:
        if self.__painter is None:
            raise ValueError("Painter has not yet been set!")
        return self.__painter

    @property
    def main_widget(self) -> ui.MainWidget:
        if self.__main_widget is None:
            raise ValueError("main widget has not yet been set!")
        return self.__main_widget

    def set_painter(self, painter: renderer.GraphicsScreen):
        self.__painter = painter

    def set_main_widget(self, main_widget: ui.MainWidget):
        self.__main_widget = main_widget
        self.entities.add_ship_log()

    def handle_keys(self, on_tick: bool):
        if (
            self.game_over or self.lock_movement
        ):  # if game is over or movement is locked, don't allow movement
            return
        if on_tick:
            if Qt.Key.Key_Shift not in self.held_keys:  # hold shift to move faster
                return

        dx = 0
        dy = 0

        valid_move = False

        did_disembark = False

        for key in self.held_keys:
            if key == Qt.Key.Key_Up:
                dy -= 1
            elif key == Qt.Key.Key_Down:
                dy += 1
            elif key == Qt.Key.Key_Left:
                dx -= 1
            elif key == Qt.Key.Key_Right:
                dx += 1
            elif key == Qt.Key.Key_Space:
                did_disembark = True

        was_valid_move = False
        if dx != 0 or dy != 0:
            if self.entities.move_player((dx, dy)):
                was_valid_move = True
            valid_move = True

        if did_disembark:
            if self.entities.toggle_on_land():
                was_valid_move = True
            self.main_widget.right_pannel.update_embark_text()
            valid_move = True

        if valid_move:
            self.entities.done_p_move(was_valid_move)

    def on_tick(self):
        # fps related calculations
        self.previous_frame = self.current_frame
        self.current_frame = time.time_ns()

        delta = self.current_frame - self.previous_frame
        if delta == 0:
            delta = 0.000000000001
        self.deltatime = delta / 1_000_000_000

        if self.frame % 10 == 0:
            # print(f"FPS:{1_000_000_000 / delta}")
            pass

        self.frame += 1  # increment frame counter
        self.handle_keys(on_tick=True)  # handle keys on tick

        self.painter.draw()  # draw the board

    def key_press(self, key: int):
        self.held_keys.add(key)
        self.handle_keys(on_tick=False)

    def key_release(self, key: int):
        if key in self.held_keys:
            self.held_keys.remove(key)

    def end_game(self, cause_of_death: str):
        for (
            player
        ) in self.entities.player.get_enabled_players():  # disable and hide all players
            player.enabled = False
            player.visible = False

        self.game_over = True

        self.main_widget.right_pannel.setEnabled(False)

        self.game_over_screen = ui.GameOverScreen(self, cause_of_death)
        self.game_over_screen.show()
