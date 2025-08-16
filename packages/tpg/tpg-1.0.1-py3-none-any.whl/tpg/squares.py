from __future__ import annotations

import math
from typing import Any, Generator, TypeVar

from PySide6 import QtCore, QtGui

from tpg import game

Color = tuple[int, int, int] | tuple[int, int, int, int]

directions: list[tuple[int, int]] = [
    (-1, 0),  # U
    (0, -1),  # L
    (0, 1),  # R
    (1, 0),  # D
]


directions_corners = [
    (-1, 0),  # U
    (0, -1),  # L
    (0, 1),  # R
    (1, 0),  # D
    (-1, -1),  # UL
    (-1, 1),  # UR
    (1, -1),  # DL
    (1, 1),  # DR
]


class Square:
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
    ):
        self.game = game
        self.x = x
        self.y = y

        self.create_render_cache()

        self.brush: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255))

        self.pen: QtGui.QPen = QtGui.QPen(QtGui.QColor(0, 0, 0))

        self.visible = True

    def create_render_cache(self):
        """Creating rects every frame is slow, so cache them here."""
        self.__rect_cache: dict[tuple[int, int, int], QtCore.QRect] = {}

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    @staticmethod
    def isinstance_subclass(obj: Any, t2: type):
        if isinstance(obj, t2):
            return True
        if issubclass(obj, t2):
            return True

        return False

    @staticmethod
    def from_square(square: Square, t: type[T]) -> T:
        return t(square.game, square.x, square.y)

    @property
    def texture(self) -> QtGui.QPixmap | None:
        return None

    def draw(
        self,
        painter: QtGui.QPainter,
        spacing: int,
    ) -> bool:
        if not self.visible:
            return False

        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        key = (self.x, self.y, spacing)

        rect = self.__rect_cache.get(key)
        if rect is None:
            x_pos = self.x * spacing
            y_pos = self.y * spacing

            rect = QtCore.QRect(x_pos, y_pos, spacing, spacing)
            self.__rect_cache[key] = rect

        if self.texture is not None:
            painter.drawPixmap(rect, self.texture)
        else:
            painter.drawRect(rect)

        return True

    def get_corners(self) -> list[tuple[int, int]]:
        return [
            (0, 0),
            (0, self.game.terrain.height - 1),
            (self.game.terrain.width - 1, 0),
            (self.game.terrain.width - 1, self.game.terrain.height - 1),
        ]

    def get_corner_squares(self) -> Generator[Square, None, None]:
        for corner in self.get_corners():
            yield self.game.terrain[corner[0]][corner[1]]

    def get_adjacent_squares(
        self,
        include_corners: bool = True,
        radius: int = 1,
        direction: tuple[int, int] | None = None,
        include_self: bool = True,
        include_equals: bool = True,
    ) -> Generator[Square, None, None]:
        if radius == 0:
            yield self.game.terrain[self.x][self.y]

        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                if not include_corners:
                    if x != 0 and y != 0:
                        continue
                if not include_self:
                    if x == 0 and y == 0:
                        continue

                if (
                    direction is not None
                ):  # complicated stuff if direction is specified, works using y=x and y=-x lines
                    if direction[0] < 0 or direction[1] < 0:
                        y_val = -y
                        x_val = x
                    else:
                        y_val = y
                        x_val = -x

                    if x_val > y_val:
                        continue

                    if not include_equals:
                        if abs(x_val) == abs(y_val):
                            continue

                    if direction in [(0, -1), (1, 0)]:
                        if x < y:
                            continue
                    if direction in [(0, 1), (-1, 0)]:
                        if x > y:
                            continue

                new_x = x + self.x
                new_y = y + self.y
                if new_x < 0 or new_y < 0:
                    continue
                if (
                    new_x >= self.game.terrain.width
                    or new_y >= self.game.terrain.height
                ):
                    continue

                square = self.game.terrain[new_x][new_y]

                yield square

    def get_adjacent_t(
        self,
        t: type[T],
        include_corners: bool = True,
        radius: int = 1,
        direction: tuple[int, int] | None = None,
        include_self: bool = True,
        include_equals: bool = True,
    ) -> Generator[T, None, None]:
        for square in self.get_adjacent_squares(
            include_corners, radius, direction, include_self, include_equals
        ):
            if isinstance(square, t):
                yield square

    def is_adjacent_to(
        self,
        other: Square,
        include_corners: bool = True,
        radius: int = 1,
        direction: tuple[int, int] | None = None,
        include_equals: bool = True,
    ):
        dx = self.x - other.x
        dy = self.y - other.y

        if direction is not None:
            if direction[0] < 0 or direction[1] < 0:
                y_val = -dy
                x_val = dx
            else:
                y_val = dy
                x_val = -dx

            if x_val > y_val:
                return False

            if not include_equals:
                if abs(x_val) == abs(y_val):
                    return False

            if direction in [(0, -1), (1, 0)]:
                if dx < dy:
                    return False
            if direction in [(0, 1), (-1, 0)]:
                if dx > dy:
                    return False

        dx = abs(dx)
        dy = abs(dy)

        is_adjacent_corner = dx <= radius and dy <= radius
        if not is_adjacent_corner:
            return False

        if include_corners:
            return True
        else:
            return dx == 0 or dy == 0

    def on_top_of(self, other: Square):
        return self.x == other.x and self.y == other.y

    def is_adjacent_to_t(
        self,
        other_t: type[Square],
        self_t: type[Square] | None = None,
        include_corners: bool = True,
        radius: int = 1,
        direction: tuple[int, int] | None = None,
        include_self: bool = True,
        include_equals: bool = True,
    ):
        if self_t is not None:
            if not isinstance(self, self_t):
                return False
        return bool(  # check for one or more adjacent squares of type other_t
            next(
                self.get_adjacent_t(
                    other_t,
                    include_corners,
                    radius,
                    direction,
                    include_self,
                    include_equals,
                ),
                None,
            )
        )

    def is_in_corners(self, radius: int = 1):  # check if square is in the corners
        for sq in self.get_corner_squares():
            if sq.is_adjacent_to(self, radius=radius - 1):
                return True
        return False

    def __hash__(self):
        return hash((self.x, self.y))  # hash based on x and y. used in sets


T = TypeVar("T", bound=Square)


class Water(Square): ...


class Ocean(Water):
    def __init__(self, game: game.Game, x: int, y: int):
        super().__init__(game, x, y)

        self.brush = QtGui.QBrush(QtGui.QColor(29, 162, 216))  # blue


class Lake(Water):
    def __init__(self, game: game.Game, x: int, y: int):
        super().__init__(game, x, y)

        self.brush = QtGui.QBrush(QtGui.QColor(19, 122, 255))  # dark blue


class Land(Square):
    def __init__(self, game: game.Game, x: int, y: int):
        super().__init__(game, x, y)

        self.brush = QtGui.QBrush(QtGui.QColor(0, 224, 0))  # green


class Beach(Land):
    def __init__(self, game: game.Game, x: int, y: int):
        super().__init__(game, x, y)

        self.brush = QtGui.QBrush(QtGui.QColor(255, 255, 200))  # pale yellow


class PirateCount(Square):
    def __init__(
        self,
        game: game.Game,
        x: int,
        y: int,
        pirate_count: int,
        trader_count: int,
        direction: tuple[int, int],
        is_close: bool,
    ):
        super().__init__(game, x, y)

        self.pirate_count = pirate_count
        self.trader_count = trader_count
        self.direction = direction
        self.is_close = is_close

        self.visible = (
            self.pirate_count + self.trader_count
        ) > 0  # only show if there are pirates or traders

    @property
    def border_color(self) -> Color | None:
        if self.is_close:
            return (200, 0, 64)  # red border for close squares
        return None

    @property
    def fill_color(self) -> Color:
        opacity = 1 - 1 / (
            self.pirate_count + self.trader_count + 1
        )  # opacity based on count
        opacity *= 255
        opacity = int(opacity)

        if self.direction == (0, -1):  # North
            return (182, 98, 40, opacity)  # orange
        if self.direction == (1, 0):  # East
            return (88, 134, 58, opacity)  # green
        if self.direction == (0, 1):  # South
            return (38, 92, 140, opacity)  # blue
        if self.direction == (-1, 0):  # West
            return (196, 196, 2, opacity)  # yellows
        return (255, 255, 255, opacity)  # white

    def draw(
        self,
        painter: QtGui.QPainter,
        spacing: int,
    ):
        self.brush = QtGui.QBrush(QtGui.QColor(*self.fill_color))

        if self.border_color is None:
            self.pen = QtGui.QPen()
            self.pen.setStyle(QtGui.Qt.PenStyle.NoPen)
        else:
            self.pen = QtGui.QPen(QtGui.QColor(*self.border_color))

        res = super().draw(painter, spacing)
        if not res:
            return False

        if self.is_close:
            text = f"{self.pirate_count} {self.trader_count}"
            font_size = math.ceil(spacing / 2)
        else:
            text = f"{self.pirate_count}"
            font_size = spacing

        x_pos = self.x * spacing
        y_pos = self.y * spacing

        rect = QtCore.QRect(x_pos, y_pos, spacing, spacing)

        painter.setPen(QtGui.QColor(0, 0, 0))

        font = QtGui.QFont()
        font.setPixelSize(font_size)

        painter.setFont(font)

        painter.drawText(rect, text, QtCore.Qt.AlignmentFlag.AlignCenter)

        return True


class SeaMonsterRumour(Square):
    def __init__(self, game: game.Game, x: int, y: int):
        super().__init__(game, x, y)

        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtGui.Qt.BrushStyle.NoBrush)

        self.pen = QtGui.QPen(QtGui.QColor(200, 0, 64))

    def draw(
        self,
        painter: QtGui.QPainter,
        spacing: int,
    ):
        res = super().draw(painter, spacing)
        if not res:
            return False

        text = "R"

        x_pos = self.x * spacing
        y_pos = self.y * spacing + 1

        rect = QtCore.QRect(x_pos, y_pos, spacing, spacing)

        painter.setPen(QtGui.QColor(0, 0, 0))

        font = QtGui.QFont()
        font.setPixelSize(spacing)

        painter.setFont(font)

        painter.drawText(rect, text, QtCore.Qt.AlignmentFlag.AlignCenter)

        return True
