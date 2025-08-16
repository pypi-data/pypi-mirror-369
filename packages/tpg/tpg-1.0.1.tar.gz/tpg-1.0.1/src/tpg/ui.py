from __future__ import annotations

import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QKeyEvent

from tpg import game, renderer, upgrade, entities


class UpgradeScreen(QtWidgets.QWidget):
    def __init__(self, game: game.Game):
        super().__init__()

        self.game = game

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.gbox = QtWidgets.QGroupBox("Upgrades")
        self.gbox_layout = QtWidgets.QVBoxLayout(self.gbox)
        self._layout.addWidget(self.gbox)

        headers = ["Upgrade", "Cost", "Effect"]

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.table.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.table.itemDoubleClicked.connect(self.buy_upgrade)

        self.gbox_layout.addWidget(self.table)

        self.upgrades = self.game.upgrades.copy()

        self.populate_table()

        self.upgrade_button = QtWidgets.QPushButton()
        self.upgrade_button.clicked.connect(self.buy_upgrade)
        self.gbox_layout.addWidget(self.upgrade_button)

        self.update_table()

        self.table.itemSelectionChanged.connect(self.on_select_change)

        self.on_select_change()

    def reset(self):
        self.upgrades = self.game.upgrades.copy()
        self.populate_table()
        self.update_table()
        self.on_select_change()

    def update_button(self, upgrade: upgrade.Upgrade | None):
        self.upgrade_button.setEnabled(upgrade is not None)
        if upgrade is None:
            if not self.upgrades:
                text = "No Upgrades Available"
            else:
                text = "No Upgrade Selected"
        else:
            text = f"Buy {upgrade.name} for {upgrade.cost} gold"
        self.upgrade_button.setText(text)

    def populate_table(self):
        # clear rows
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

        for i, upgrade in enumerate(self.upgrades):
            name = upgrade.name
            cost = upgrade.cost
            effect = upgrade.effect

            self.table.insertRow(i)

            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(cost)))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(effect))

        self.table.resizeColumnsToContents()

    def on_select_change(self):
        res = self.get_selected_upgrade()
        if res is None:
            self.update_button(None)
            return
        _, upgrade = res
        self.update_button(upgrade)

    def buy_upgrade(self):
        res = self.get_selected_upgrade()
        if res is None:
            return
        index, upgrade = res
        res = self.game.entities.player.try_upgrade(upgrade)
        if not res:
            self.table.removeRow(index)
            self.table.resizeColumnsToContents()
            self.upgrades.pop(index)
            if self.upgrades:
                self.table.selectRow(index)
            else:
                self.update_button(None)
        else:
            self.upgrade_button.setText(res)

    def get_selected_upgrade(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            return None
        index = indexes[0].row()
        if index < 0 or index >= len(self.upgrades):
            return None
        upgrade = self.upgrades[index]
        return index, upgrade

    def update_table(self):
        in_corner = self.game.entities.player.is_in_corner()
        self.table.setEnabled(in_corner)

        if self.upgrades:
            self.upgrade_button.setEnabled(in_corner)
        else:
            self.upgrade_button.setEnabled(False)


class GameOverScreen(QtWidgets.QWidget):
    def __init__(self, game: game.Game, cause_of_death: str):
        self.game = game
        self.cause_of_death = cause_of_death

        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle("Game Over")

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.group_box = QtWidgets.QGroupBox("Game Over!")
        self.group_box_layout = QtWidgets.QVBoxLayout(self.group_box)
        self._layout.addWidget(self.group_box)

        self.group_box_layout.addWidget(QtWidgets.QLabel(self.cause_of_death))

        self.gold_widget = QtWidgets.QGroupBox()
        self.gold_widget_layout = QtWidgets.QHBoxLayout(self.gold_widget)

        self.group_box_layout.addWidget(self.gold_widget)

        gold_text = QtWidgets.QLabel("Final Gold:")
        self.gold_widget_layout.addWidget(gold_text)

        self.gold_widget_layout.addStretch()

        gold_amount = QtWidgets.QLabel(str(self.game.entities.player.gold))
        self.gold_widget_layout.addWidget(gold_amount)

        self.group_box_layout.addStretch()


class ShipLog(QtWidgets.QWidget):
    def __init__(self, game: game.Game):
        super().__init__()

        self.game = game

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)
        self._layout.addWidget(self.text_area)

    def add_text(self, text: str):
        text += "\n"
        self.text_area.insertPlainText(text)
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )


class RightPannel(QtWidgets.QWidget):
    def __init__(self, game: game.Game):
        super().__init__()

        self.game = game

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.create_gold_box()
        self.create_buttons()
        self.create_update_screen()

        self.create_ship_log()

        self._layout.addStretch()

    def create_update_screen(self):
        self.upgrade_screen = UpgradeScreen(self.game)
        self._layout.addWidget(self.upgrade_screen)

    def create_gold_box(self):
        self.gold_box = QtWidgets.QGroupBox()
        self.gold_box_layout = QtWidgets.QHBoxLayout(self.gold_box)
        self.gold_box_layout.addWidget(
            QtWidgets.QLabel("Gold:"),
        )
        self.gold_box_layout.addStretch()
        self.gold_num_label = QtWidgets.QLabel(str(self.game.entities.player.gold))
        self.gold_box_layout.addWidget(self.gold_num_label)
        self._layout.addWidget(self.gold_box)

    def create_ship_log(self):
        self.ship_log_box = QtWidgets.QGroupBox("Ship Log")
        self.ship_log_box_layout = QtWidgets.QVBoxLayout(self.ship_log_box)
        self._layout.addWidget(self.ship_log_box)
        self.ship_log = ShipLog(self.game)
        self.ship_log_box_layout.addWidget(self.ship_log)

    def create_directional_button(self, text: str, x: int, y: int):
        row = y + 1
        col = x + 1

        button = QtWidgets.QPushButton(text)
        button.clicked.connect(lambda: self.button_clicked(x, y))

        self.buttons_box_layout.addWidget(button, row, col)

    def button_clicked(self, x: int, y: int):
        was_valid = self.game.entities.move_player((x, y))
        self.game.entities.done_p_move(was_valid)

    def embark_clicked(self):
        was_valid = self.game.entities.toggle_on_land()
        self.game.entities.done_p_move(was_valid)

        self.update_embark_text()

    def create_buttons(self):
        self.buttons_box = QtWidgets.QGroupBox()
        self.buttons_box_layout = QtWidgets.QGridLayout(self.buttons_box)

        dirs: list[tuple[str, tuple[int, int]]] = [
            ("NW", (-1, -1)),
            ("N", (0, -1)),
            ("NE", (1, -1)),
            ("E", (1, 0)),
            ("SE", (1, 1)),
            ("S", (0, 1)),
            ("SW", (-1, 1)),
            ("W", (-1, 0)),
        ]

        for dir in dirs:
            self.create_directional_button(dir[0], *dir[1])

        self.embark_button = QtWidgets.QPushButton()
        self.embark_button.clicked.connect(self.embark_clicked)

        self.update_embark_text()

        self.buttons_box_layout.addWidget(self.embark_button, 1, 1)

        self._layout.addWidget(self.buttons_box)

    def update_embark_text(self):
        if self.game.entities.player.on_land():
            text = "EMBARK"
        else:
            text = "DISEMBARK"

        self.embark_button.setText(text)

    def update_gold_text(self):
        gold = self.game.entities.player.gold

        self.gold_num_label.setText(str(gold))


class TradePopup(QtWidgets.QWidget):
    investSubmitted = QtCore.Signal(int)
    investCancelled = QtCore.Signal()

    def disconnect_signals(self):
        self.investSubmitted.disconnect()
        self.investCancelled.disconnect()

    def __init__(self, game: game.Game):
        self.game = game
        super().__init__()

        self.init_ui()
        self.hide()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self.ask_box = QtWidgets.QGroupBox("Trade Offer")
        self.ask_box_layout = QtWidgets.QVBoxLayout(self.ask_box)
        self._layout.addWidget(self.ask_box)

        self.label = QtWidgets.QLabel("A friendly tribe is offering you a trade!")
        self.ask_box_layout.addWidget(self.label)

        self.investment_layout = QtWidgets.QHBoxLayout()
        self.ask_box_layout.addLayout(self.investment_layout)

        self.investment_label = QtWidgets.QLabel("Investment Amount:")
        self.investment_layout.addWidget(self.investment_label)

        self.investment_spinbox = QtWidgets.QSpinBox()
        self.investment_spinbox.setMinimum(self.game.min_invest)
        self.investment_spinbox.setMaximum(self.game.max_invest)
        self.investment_layout.addWidget(self.investment_spinbox)

        self.investment_submit = QtWidgets.QPushButton("INVEST")
        self.ask_box_layout.addWidget(self.investment_submit)
        self.investment_submit.clicked.connect(self.investment_submitted)

        self.investment_cancel = QtWidgets.QPushButton("REJECT")
        self.ask_box_layout.addWidget(self.investment_cancel)
        self.investment_cancel.clicked.connect(self.investment_cancelled)

        self.ask_box_layout.addStretch()

        self._layout.addStretch()

    def set_max_money(self):
        gold = self.game.entities.player.gold
        enough_gold = gold >= self.game.min_invest

        self.investment_submit.setEnabled(enough_gold)
        if not enough_gold:
            self.investment_submit.setText("Not enough gold!")
        else:
            self.investment_submit.setText("INVEST")

        max_gold = min(self.game.max_invest, gold)
        max_gold = max(self.game.min_invest, max_gold)
        self.investment_spinbox.setMaximum(max_gold)

    def start_investment(self):
        self.set_max_money()
        self.investment_spinbox.setValue(self.game.min_invest)
        self.show()
        self.game.main_widget.releaseKeyboard()
        self.investment_spinbox.grabKeyboard()

    def investment_submitted(self):
        self.investment_spinbox.releaseKeyboard()
        self.game.main_widget.grabKeyboard()

        self.investment_spinbox.clearFocus()

        self.investSubmitted.emit(self.investment_spinbox.value())

        self.hide()

    def investment_cancelled(self):
        self.investment_spinbox.releaseKeyboard()
        self.game.main_widget.grabKeyboard()

        self.investment_spinbox.clearFocus()

        self.investCancelled.emit()

        self.hide()


class TraderPopup(QtWidgets.QWidget):
    fightSubmitted = QtCore.Signal()
    fightIgnored = QtCore.Signal()

    def disconnect_signals(self):
        self.fightSubmitted.disconnect()
        self.fightIgnored.disconnect()

    def __init__(self, game: game.Game):
        self.game = game
        super().__init__()

        self.init_ui()
        self.hide()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self.ask_box = QtWidgets.QGroupBox("Trader Choice")
        self.ask_box_layout = QtWidgets.QVBoxLayout(self.ask_box)
        self._layout.addWidget(self.ask_box)

        self.label = QtWidgets.QLabel("You found a trader!")
        self.ask_box_layout.addWidget(self.label)

        self.fight_layout = QtWidgets.QHBoxLayout()
        self.ask_box_layout.addLayout(self.fight_layout)

        self.fight_label = QtWidgets.QLabel("Make a choice:")
        self.fight_layout.addWidget(self.fight_label)

        self.fight_submit = QtWidgets.QPushButton("FIGHT")
        self.ask_box_layout.addWidget(self.fight_submit)
        self.fight_submit.clicked.connect(self.fight_submitted)

        self.ignore_cancel = QtWidgets.QPushButton("IGNORE")
        self.ask_box_layout.addWidget(self.ignore_cancel)
        self.ignore_cancel.clicked.connect(self.fight_ignored)

        self.ask_box_layout.addStretch()

        self._layout.addStretch()

    def fight_submitted(self):
        self.fightSubmitted.emit()

        self.hide()

    def fight_ignored(self):
        self.fightIgnored.emit()

        self.hide()

    def start_choice(self, trader: entities.trader.Trader):
        self.show()
        self.trader = trader


class LookoutLog(QtWidgets.QWidget):
    def __init__(self, game: game.Game):
        super().__init__()

        self.game = game
        self.hide()

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.main_box = QtWidgets.QGroupBox()
        self._layout.addWidget(self.main_box)

        self.box_layout = QtWidgets.QVBoxLayout(self.main_box)

        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)
        self.box_layout.addWidget(self.text_area)

    def add_text(self, text: str):
        previous_text = self.text_area.toPlainText()

        text += "\n"
        self.text_area.insertPlainText(text)
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )
        if previous_text:
            self.text_area.setFixedHeight(
                self.text_area.document().size().toSize().height()
            )

    def clear_text(self):
        self.text_area.clear()


class BottomPannel(QtWidgets.QWidget):
    def __init__(self, game: game.Game):
        self.game = game
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.trade_popup = TradePopup(self.game)
        self._layout.addWidget(self.trade_popup)

        self.trader_popup = TraderPopup(self.game)
        self._layout.addWidget(self.trader_popup)

        self.lookout_log = LookoutLog(self.game)
        self._layout.addWidget(self.lookout_log)

        self._layout.addStretch()


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.grabKeyboard()

        self.create_game()

        self.init_ui()

        self.init_other()

    def set_main_window(self, main_window: MainWindow):
        self.main_window = main_window

    def create_game(self):
        self.game = game.Game()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.hoz_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.vir_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        self._layout.addWidget(self.vir_splitter)

        self.vir_splitter.addWidget(self.hoz_splitter)

        self.wrapper_painter = renderer.GamePainterWrapper(self)

        self.painter = self.wrapper_painter.game_painter
        self.painter.set_game(self.game)

        self.hoz_splitter.addWidget(self.wrapper_painter)

        self.right_pannel = RightPannel(self.game)

        self.hoz_splitter.addWidget(self.right_pannel)

        self.bottom_pannel = BottomPannel(self.game)

        self.vir_splitter.addWidget(self.bottom_pannel)

        width = self.width()

        self.hoz_splitter.setSizes([int(width * 3 / 4), width // 4])

    def init_other(self):
        self.game.set_painter(self.painter)
        self.game.set_main_widget(self)

        self.clock = QtCore.QTimer()
        self.clock.setInterval(1000 // self.game.fps)
        self.clock.timeout.connect(self.clock_tick)

        self.clock.start()

    def update_fps(self):
        self.clock.setInterval(1000 // self.game.fps)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_F11:  # toggle fullscreen
            if self.main_window.isFullScreen():
                self.main_window.showNormal()
            else:
                self.main_window.showFullScreen()

        self.game.key_press(event.key())

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.game.key_release(event.key())

    def clock_tick(self):
        self.game.on_tick()


class Preferences(QtWidgets.QWidget):  # unused
    def __init__(self, game: game.Game):
        self.game = game
        super().__init__()

        self.setWindowTitle("Preferences")

        self.init_ui()

        self.game.main_widget.releaseKeyboard()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.game.main_widget.grabKeyboard()

    def init_ui(self):
        self._layout = QtWidgets.QVBoxLayout(self)

        self.main_box = QtWidgets.QGroupBox()
        self._layout.addWidget(self.main_box)

        self.main_layout = QtWidgets.QVBoxLayout(self.main_box)

        self.update_items()

        self.save_button = QtWidgets.QPushButton("Apply")
        self.save_button.clicked.connect(self.apply)
        self._layout.addWidget(self.save_button)

    def update_items(self):
        # delete all items
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            item.widget().deleteLater()

        self.main_layout.setStretch(0, 0)

        self.dbg = self.add_item_bool("Debug Mode", self.game.debug)
        self.fps = self.add_item_int(
            "FPS",
            self.game.fps,
            min=1,
        )

        self.min_invest = self.add_item_int(
            "Minimum Investment",
            self.game.min_invest,
        )

        self.max_invest = self.add_item_int(
            "Maximum Investment",
            self.game.max_invest,
        )

        self.invest_interval = self.add_item_int(
            "Investment Interval",
            self.game.investment_interval,
        )

        self.grid_size = self.add_item_int_list(
            "Grid Size",
            list(self.game.grid_size),
            ["Width", "Height"],
            [(1, None), (1, None)],
        )

        self.main_layout.addStretch()

    def apply(self):
        self.game.debug = self.dbg.isChecked()
        self.game.fps = self.fps.value()
        self.game.min_invest = self.min_invest.value()
        self.game.max_invest = self.max_invest.value()
        self.game.investment_interval = self.invest_interval.value()

        width = self.grid_size[0].value()
        height = self.grid_size[1].value()

        self.game.grid_size = (width, height)

    def add_item_int_list(
        self,
        key: str,
        values: list[int],
        keys: list[str],
        mins_maxes: list[tuple[int | None, int | None]] | None,
    ) -> list[QtWidgets.QSpinBox]:
        widgets: list[QtWidgets.QGroupBox] = []
        spin_boxes: list[QtWidgets.QSpinBox] = []

        for i, (keyv, value) in enumerate(zip(keys, values)):
            box_widget = QtWidgets.QGroupBox()
            box_widget_layout = QtWidgets.QHBoxLayout(box_widget)

            w1 = QtWidgets.QLabel(keyv)
            w2 = QtWidgets.QSpinBox()
            if mins_maxes is not None:
                min, max = mins_maxes[i]
                if min is None:
                    min = -(2**31)
                if max is None:
                    max = (2**31) - 1
                w2.setMinimum(min)
                w2.setMaximum(max)

            w2.setValue(value)

            box_widget_layout.addWidget(w1)
            box_widget_layout.addWidget(w2)

            widgets.append(box_widget)

            spin_boxes.append(w2)

        self.add_item_widgets(key, *widgets)

        return spin_boxes

    def add_item_str(self, key: str, value: str) -> QtWidgets.QLineEdit:
        value_widget = QtWidgets.QLineEdit(value)
        self.add_item_widgets(key, value_widget)

        return value_widget

    def add_item_bool(self, key: str, value: bool) -> QtWidgets.QCheckBox:
        value_widget = QtWidgets.QCheckBox()
        value_widget.setChecked(value)
        self.add_item_widgets(key, value_widget)

        return value_widget

    def add_item_int(
        self, key: str, value: int, min: int | None = None, max: int | None = None
    ) -> QtWidgets.QSpinBox:
        value_widget = QtWidgets.QSpinBox()

        if min is None:
            minv = -(2**31)
        else:
            minv = min

        value_widget.setMinimum(minv)

        if max is None:
            maxv = 2**31 - 1
        else:
            maxv = max

        value_widget.setMaximum(maxv)

        value_widget.setValue(value)
        self.add_item_widgets(key, value_widget)

        return value_widget

    def add_item_widgets(self, key: str, *value_widgets: QtWidgets.QWidget):
        h_layout = QtWidgets.QHBoxLayout()

        self.main_layout.addLayout(h_layout)

        h_layout.addWidget(QtWidgets.QLabel(key))

        for value_widget in value_widgets:
            h_layout.addWidget(value_widget)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(900, 700)
        self.init_ui()

    def init_ui(self):
        self.main_widget = MainWidget()
        self.main_widget.set_main_window(self)
        self.setCentralWidget(self.main_widget)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = QtWidgets.QMenuBar()

        file_menu = QtWidgets.QMenu("File", menu_bar)

        # settings_action = QtGui.QAction("Preferences", file_menu)
        # settings_action.triggered.connect(self.open_preferences)
        # file_menu.addAction(settings_action)  # type: ignore

        quit_action = QtGui.QAction("Quit", file_menu)
        quit_action.triggered.connect(self.exit)
        file_menu.addAction(quit_action)  # type: ignore

        menu_bar.addMenu(file_menu)

        # game_menu = QtWidgets.QMenu("Game", menu_bar)

        # regenerate_action = QtGui.QAction("Regenerate Board", game_menu)
        # regenerate_action.setShortcut("Ctrl+R")
        # regenerate_action.triggered.connect(self.regenerate_board)
        # game_menu.addAction(regenerate_action)  # type: ignore

        # menu_bar.addMenu(game_menu)

        self.setMenuBar(menu_bar)

    def regenerate_board(self):
        self.main_widget.game.create_game()

    def exit(self):
        QtCore.QCoreApplication.quit()

    def open_preferences(self):
        self.preferences = Preferences(self.main_widget.game)
        self.preferences.show()


def run():
    app = QtWidgets.QApplication()
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
