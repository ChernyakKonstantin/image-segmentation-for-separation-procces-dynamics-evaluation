# TODO Добавить темную тему
# TODO Добавить печать тренда

import datetime as dt
import sys
from typing import Tuple

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QActionGroup, QMenu, QPushButton
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QMenuBar, QStatusBar, QVBoxLayout

from interactive_chart import BaseTimeSeries
from interactive_mask_display import InteractiveMaskDisplay


class Client:
    """Класс TCP-клиента, опрашивающего сервер для получения результатов сегментации."""

    def __init__(self, ip: str, port: int):
        # Заглушка
        pass

    def receive(self):
        """Метод получения данных от сервера."""
        # Заглушка
        image: np.ndarray = np.random.randint(0, 255, (360, 640, 3), dtype='uint8')
        mask: np.ndarray = np.random.randint(0, 255, (360, 640, 3), dtype='uint8')
        cur_datetime = dt.datetime.now()
        values: Tuple[float, float, float] = tuple(np.random.random(3))
        return image, mask, cur_datetime, values


class CentralWidget(QWidget):
    """Обязательный виджет Qt-приложения. Используется в QMainWindow."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._setup_menu_pbtn()

        self.chart = BaseTimeSeries()
        self.segmented_img = InteractiveMaskDisplay('Segmentation')

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.segmented_img)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.chart)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.menu_pbtn, 1, Qt.AlignLeft)

        self.setLayout(v_layout)

    def _setup_visibility_menu(self):
        self.menu = QMenu('Select visible layers')
        self._action_group = QActionGroup(self)
        self._action_group.setExclusive(False)

        self._visibility_menu_actions = {}
        for action_name in ['All', 'Oil', 'Emulsion', 'Water']:
            action = self.menu.addAction(action_name)
            action.setCheckable(True)
            if action_name == 'All':
                action.triggered.connect(self._on_show_all_trigger)
            else:
                action.triggered.connect(self._on_visibility_menu_trigger)
                self._action_group.addAction(action)
            self._visibility_menu_actions[action_name] = action

    def _setup_menu_pbtn(self):
        self._setup_visibility_menu()
        self.menu_pbtn = QPushButton('Visible layers')
        self.menu_pbtn.setMenu(self.menu)

    def _on_show_all_trigger(self):
        """Обработчик нажатия на кнопку All"""
        if self._visibility_menu_actions['All'].isChecked():
            for action in self._action_group.actions():
                action.setChecked(True)
        else:
            for action in self._action_group.actions():
                action.setChecked(False)

    def _on_visibility_menu_trigger(self):
        """Обработчик нажатия на кнопки"""
        if all([action.isChecked() for action in self._action_group.actions()]):
            self._visibility_menu_actions['All'].setChecked(True)
        else:
            self._visibility_menu_actions['All'].setChecked(False)


class MainWindow(QMainWindow):
    """Обязательный виджет Qt-приложения. Используется в QApplication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Separator Dynamics Estimator')

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        self.menu_bar.addAction('Quit', self.close)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.show()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tcp_client_setup()
        self.main_window = MainWindow()

    def _tcp_client_setup(self):
        """Инициализация TCP-клиента"""
        self._tcp_client = Client('localhost', 8080)
        self._tcp_client_timer = QTimer()
        self._tcp_client_timer.setInterval(100)
        self._tcp_client_timer.timeout.connect(self._handle_tcp_client)
        self._tcp_client_timer.start()

    def _handle_tcp_client(self):
        """Обработчик TCP-клиента"""
        image, mask, cur_time, values = self._tcp_client.receive()
        self.main_window.central_widget.chart.add_new_values((cur_time, values))
        self.main_window.central_widget.segmented_img.draw(image)


app = Application(sys.argv)
sys.exit(app.exec_())
