from __future__ import annotations

from PySide6 import QtGui, QtWidgets, QtCore

from tpg import game


class GraphicsScreen(QtWidgets.QGraphicsScene):
    def __init__(self, parent: GamePainterWrapper):
        super().__init__(parent)

        self._parent = parent
        self.curr_size: QtCore.QSize = parent.get_size()

        self.pixmap_size = self.curr_size

        self.view = QtWidgets.QGraphicsView(self, parent)
        self.view.show()
        self.view.resize(self.curr_size)

        self.pixmap = QtGui.QPixmap(self.pixmap_size)

        self.addPixmap(self.pixmap)

        self.painter = QtGui.QPainter()

        self.view.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.view.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

    def calculate_true_dims(self):
        width = self.game.terrain.width
        height = self.game.terrain.height

        spacing_x = int(self.curr_size.width() / width)  # get the spacing for the width
        spacing_y = int(
            self.curr_size.height() / height
        )  # get the spacing for the height

        spacing = min(spacing_x, spacing_y)  # get the minimum spacing

        true_width = spacing * width
        true_height = spacing * height
        return true_width, true_height

    def set_game(self, game: game.Game):
        self.game = game

        self._parent.setMinimumWidth(self.game.terrain.width * 2)
        self._parent.setMinimumHeight(self.game.terrain.height * 2)

        self.resize()

    def draw(self):
        self.clear()  # clear the scene
        self.resize()

        self.painter.begin(self.pixmap)

        for x, y in self.game.terrain.all_positions:
            sq = self.game.terrain[x][y]
            sq.draw(  # draw the square
                self.painter,
                self.spacing,
            )

        for entity in self.game.entities:
            entity.draw(self.painter, self.spacing)  # draw the entity

        if self.game.entities.has_pirate_lookout():
            for pirate_sq in self.game.entities.pirate_lookout:
                pirate_sq.draw(self.painter, self.spacing)  # draw the pirate lookout

        for sq in self.game.entities.rumours:
            sq.draw(self.painter, self.spacing)  # draw sea monster rumours

        if self.game.entities.popup.text_queue:
            self.game.entities.popup.draw(self.painter, self.spacing)  # draw the popup

        self.addPixmap(self.pixmap)  # add the pixmap to the scene
        self.painter.end()  # end the painting

    def resize(self):
        size = self._parent.get_size()
        if size == self.curr_size:
            return

        self.curr_size = size
        self.view.resize(size)

        true_width, true_height = self.calculate_true_dims()

        self.view.setSceneRect(
            -(self.curr_size.width() - true_width) // 2,
            -(self.curr_size.height() - true_height) // 2,
            self.curr_size.width(),
            self.curr_size.height(),
        )

        pixmap_size = QtCore.QSize(true_width, true_height)

        if self.pixmap_size == pixmap_size or true_width == 0 or true_height == 0:
            return
        self.pixmap_size = pixmap_size

        self.pixmap = QtGui.QPixmap(self.pixmap_size)

        spacing_x = int(self.pixmap_size.width() / self.game.terrain.width)
        spacing_y = int(self.pixmap_size.height() / self.game.terrain.height)

        self.spacing = min(spacing_x, spacing_y)


class GamePainterWrapper(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self._parent = parent

        self.init_ui()

    def init_ui(self):
        self.game_painter = GraphicsScreen(self)

    def get_size(self):
        return self.size()
