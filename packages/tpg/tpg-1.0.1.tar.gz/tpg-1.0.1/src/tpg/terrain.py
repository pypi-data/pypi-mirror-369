from __future__ import annotations
import random
from typing import Generator

from tpg import squares, game

Grid = list[list[squares.Square]]


class Terrain:
    def __init__(
        self,
        game: game.Game,
        grid_size: tuple[int, int],
        islands: list[tuple[tuple[int, int], int]],
        safe_square: tuple[int, int],
    ):
        self.game = game

        self.size = grid_size
        self.width = grid_size[0]
        self.height = grid_size[1]

        self._island_layout = islands

        self._safe_square = safe_square

        self.land_spaces: list[squares.Land] = []
        self.land_poses: set[tuple[int, int]] = set()
        self.land_poses_ls: list[tuple[int, int]] = []

        self.grid: Grid = []

    def create(self):
        self.init_grid()

        self.create_islands()

        self.punch_edge_holes()
        self.punch_lakes()

        self.make_beaches()

    def init_grid(self):
        self.grid = [
            [squares.Ocean(self.game, x, y) for y in range(self.height)]
            for x in range(self.width)
        ]  # create all ocean squares

        self.all_positions: list[tuple[int, int]] = [
            (x, y) for y in range(self.height) for x in range(self.width)
        ]

        self.all_positions_s = set(self.all_positions)

    def create_islands(self):
        layout = self._island_layout

        x_max = self.width - 1
        y_max = self.height - 1

        for (width, height), quantity in layout:
            x_min = -int(width * (1 - self.game.keep_island_on_screen_factor))
            y_min = -int(height * (1 - self.game.keep_island_on_screen_factor))

            x_max = (
                int(self.width - (width * self.game.keep_island_on_screen_factor)) - 1
            )
            y_max = (
                int(self.height - (height * self.game.keep_island_on_screen_factor)) - 1
            )

            for _ in range(quantity):
                self.place_island(x_max, y_max, width, height, x_min, y_min)

        for x, y in self.land_poses:
            square = self[x][y]
            if isinstance(square, squares.Land):
                self.land_spaces.append(square)

        self.land_poses_ls = list(self.land_poses)

    def place_island(
        self,
        x_max: int,
        y_max: int,
        width: int,
        height: int,
        x_min: int,
        y_min: int,
    ):
        x_base_pos, y_base_pos = (0, 0)
        while (
            x_base_pos < x_min
            or x_base_pos > x_max
            or y_base_pos < y_min
            or y_base_pos > x_max
            or (x_base_pos < self._safe_square[0] and y_base_pos < self._safe_square[1])
        ):
            x_base_pos = random.randint(x_min, x_max)
            y_base_pos = random.randint(y_min, y_max)

        for x in range(width):
            x_pos = x_base_pos + x

            for y in range(height):
                y_pos = y_base_pos + y

                if x_pos < 0 or x_pos > x_max or y_pos < 0 or y_pos > y_max:
                    continue

                land = squares.Land(self.game, x_pos, y_pos)
                self.land_poses.add((x_pos, y_pos))
                self.set(land)

    def get_edges(
        self, include_corners: bool = True
    ) -> Generator[squares.Land, None, None]:
        for square in self.land_spaces:
            if square.is_adjacent_to_t(
                other_t=squares.Ocean, include_corners=include_corners
            ):
                yield square

    def punch_edge_holes(self):
        for edge in list(self.get_edges()):
            roll = random.randint(1, 100)
            if roll <= self.game.edge_square_probability:
                continue
            ocean = squares.Square.from_square(
                edge, squares.Ocean
            )  # turn land to ocean
            self.set(ocean)
            self.land_spaces.remove(edge)

    def punch_lakes(self):
        for square in self.land_spaces.copy():
            if not square.is_adjacent_to_t(other_t=squares.Ocean):
                roll = random.randint(1, 100)
                if roll <= self.game.inside_square_probability:
                    continue
                lake = squares.Square.from_square(
                    square, squares.Lake
                )  # turn land to lake
                self.set(lake)
                self.land_spaces.remove(square)

    def make_beaches(self):
        for square in self.get_edges(include_corners=False):
            beach = squares.Square.from_square(
                square, squares.Beach
            )  # turn land to beach
            self.set(beach)

    def __getitem__(self, index: int) -> list[squares.Square]:
        return self.grid[index]

    def set(self, square: squares.Square):
        self.grid[square.x][square.y] = square

    def __iter__(self):
        return iter(self.grid)
