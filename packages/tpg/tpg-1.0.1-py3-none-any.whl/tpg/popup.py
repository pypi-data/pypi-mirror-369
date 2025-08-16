from __future__ import annotations

import enum
import math

from PySide6 import QtCore, QtGui

from tpg import entities, game


class Icon(enum.Enum):
    """Enum for the different icons that can be displayed in the popup."""

    PIRATE = 0
    CHEST = 1
    TRIBE = 2
    TRADER = 3


class PopUp:
    def __init__(self, game: game.Game):
        self.game = game

        self.text_queue: dict[
            str, tuple[int, list[tuple[str, Icon, entities.entity.Entity]]]
        ] = {}

        self.icons: list[QtGui.QPixmap] = []

        self.load_icons()

    def load_icons(self):
        names: list[str] = [
            "pirate-ship.png",
            "treasure-chest.png",
            "mining.png",
            "ship.png",
        ]

        for name in names:
            path = self.game.get_asset(name)
            img = QtGui.QPixmap(path)
            self.icons.append(img)

    @property
    def end_frame_count(self):
        return 120  # total frames to display the popup for

    def add_text(self, text: str, icon_id: Icon, entity: entities.entity.Entity):
        data = (text, icon_id, entity)
        ls = self.text_queue.get(entity.id)
        start_frame = self.game.frame
        if ls is None:
            self.text_queue[entity.id] = (start_frame, [data])
        else:
            ls[1].append(data)
            tupl = (start_frame, ls[1])
            self.text_queue[entity.id] = tupl

    def end(self, id: str):
        del self.text_queue[id]  # remove the popup with the given id

    def ease(self, t: float) -> float:
        return 0 if t == 0 else math.pow(4, 20 * t - 20)  # exponential easing

    def draw_text(
        self,
        painter: QtGui.QPainter,
        spacing: int,
        text: str,
        icon: QtGui.QPixmap,
        player: entities.entity.Entity,
        index: int,
        t_eased: float,
    ):
        # Compilcated function to draw the text with the icon
        x = player.x
        y = player.y

        y -= 1

        y -= index

        curr_opacity = painter.opacity()

        opacity = 1 - (index * t_eased) / 3

        painter.setOpacity(opacity)

        rect_padding = 4 * (spacing / 10)

        x_pos = x * spacing
        y_pos = y * spacing

        rect_f = QtCore.QRectF(x_pos, y_pos, 0, 0)

        aligment = QtCore.Qt.AlignmentFlag.AlignCenter

        text_rect = painter.boundingRect(rect_f, aligment, text)

        img = icon.scaledToHeight(int(text_rect.height()))

        x_pos += img.width() // 2

        text_height = text_rect.height()

        y_pos -= (text_height - spacing + rect_padding) * index

        rect_f.setY(y_pos)

        new_x_pos = x_pos - (text_rect.width() // 2) + spacing // 2

        rect = QtCore.QRectF(new_x_pos, y_pos, text_rect.width(), text_rect.height())
        larger_rect = QtCore.QRectF(
            new_x_pos - rect_padding / 2,
            y_pos - rect_padding / 2,
            text_rect.width() + rect_padding + rect_padding,
            text_rect.height() + rect_padding,
        )

        img_rect = QtCore.QRectF(
            larger_rect.x() - img.width() - rect_padding // 2,
            y_pos,
            img.width(),
            img.height(),
        )

        larger_rect.setX(img_rect.x() - rect_padding)

        curr_pen = painter.pen()
        curr_brush = painter.brush()

        color = QtGui.QColor(200, 200, 200, 100)

        pen = QtGui.QPen(color)
        pen.setStyle(QtGui.Qt.PenStyle.DashLine)

        color = QtGui.QColor(100, 100, 20, 100)
        brush = QtGui.QBrush(color)

        painter.setPen(pen)
        painter.setBrush(brush)

        painter.drawRect(larger_rect)

        painter.setBrush(curr_brush)

        painter.setPen(curr_pen)

        painter.drawText(rect, text, aligment)

        img_rect = QtCore.QRect(
            int(img_rect.x()),
            int(img_rect.y()),
            int(img_rect.width()),
            int(img_rect.height()),
        )

        painter.drawPixmap(img_rect, img)

        painter.setOpacity(curr_opacity)

    def draw_1(self, painter: QtGui.QPainter, spacing: int, id: str):
        data = self.text_queue.get(id)
        if data is None:
            return

        delta_frame = self.game.frame - data[0]

        if delta_frame > self.end_frame_count:
            self.end(id)
            return

        if not data[1]:
            return

        t = delta_frame / self.end_frame_count
        t_eased = self.ease(t)

        font = QtGui.QFont()
        font.setPixelSize(spacing)
        painter.setFont(font)

        color = QtGui.QColor(255, 255, 255, int((1 - t_eased) * 255))
        pen = QtGui.QPen(color)

        painter.setPen(pen)

        for i, (text, icon, player) in enumerate(data[1]):
            icon = self.icons[icon.value]
            self.draw_text(painter, spacing, text, icon, player, i, t_eased)

    def draw(self, painter: QtGui.QPainter, spacing: int):
        for k in self.text_queue.copy().keys():
            self.draw_1(painter, spacing, k)
