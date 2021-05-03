# TODO Добавить темную тему
# TODO Добавить печать тренда

import datetime as dt
import sys
from typing import Tuple

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget

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

        self.chart = BaseTimeSeries()
        self.segmented_img = InteractiveMaskDisplay('Segmentation')

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.segmented_img)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.chart)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)


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
