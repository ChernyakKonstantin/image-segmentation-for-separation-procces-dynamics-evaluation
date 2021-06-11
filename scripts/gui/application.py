# TODO Добавить темную тему
# TODO Добавить печать тренда

import datetime as dt
import pickle
import socket
import sys
from typing import Any
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QActionGroup, QMenu, QPushButton, QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QMenuBar, QStatusBar, QVBoxLayout
from PyQt5.QtWidgets import QApplication, QCalendarWidget, QCheckBox, QFileDialog, QLabel, QMainWindow, QTimeEdit, QLineEdit
import matplotlib.pyplot as plt
from interactive_chart import TimeSeriesChart
from interactive_mask_display import InteractiveMaskDisplay
import csv

class Client:
    """Класс TCP-клиента, опрашивающего сервер для получения результатов сегментации."""

    def __init__(self, ip: str, port: int, time_step: int):
        self.ip = ip
        self.port = port
        self.time_step = time_step

    def update_timestep(self, time_step):
        self.time_step = time_step

    def receive(self):
        """Метод получения данных от сервера."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            request = []
            while True:
                packet = s.recv(4096)
                if not packet:
                    break
                request.append(packet)
            package = pickle.loads(b"".join(request))
            image, mask, values = package

        return image, mask, self.time_step, values


class CentralWidget(QWidget):
    """Обязательный виджет Qt-приложения. Используется в QMainWindow."""

    empty_message = 'Unknown'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.chart = TimeSeriesChart()
        self.img = InteractiveMaskDisplay()
        self.segmented_img = InteractiveMaskDisplay()

        self.oil_label = QLabel(f'Oil fraction: {self.empty_message}')
        self.emulsion_label = QLabel(f'Emulsion fraction: {self.empty_message}')
        self.water_label = QLabel(f'Water fraction: {self.empty_message}')

        label_layout = QVBoxLayout()
        label_layout.addWidget(self.oil_label)
        label_layout.addWidget(self.emulsion_label)
        label_layout.addWidget(self.water_label)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.img)
        h_layout.addWidget(self.segmented_img)
        h_layout.addLayout(label_layout)
        h_layout.setAlignment(Qt.AlignLeft)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.chart)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def set_text(self, values: dict):
        self.oil_label.setText(f'Oil fraction: {round(values["oil"], 1)}%')
        self.emulsion_label.setText(f'Emulsion fraction: {round(values["emulsion"], 1)}%')
        self.water_label.setText(f'Water fraction: {round(values["water"], 1)}%')


class MainWindow(QMainWindow):
    """Обязательный виджет Qt-приложения. Используется в QApplication."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Separator Dynamics Estimator')

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Server is disconnected')

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        self.menu_bar.setNativeMenuBar(True)
        self.menu_bar.addAction('Quit', self.close)
        self.menu_bar.addSeparator()

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.showFullScreen()

    def add_menubar_action(self, action_name, callback):
        self.menu_bar.addAction(action_name, callback)
        self.menu_bar.addSeparator()


class PoolingPeriodSelector(QWidget):
    def __init__(self, callback, *args, **kwargs):
        super(PoolingPeriodSelector, self).__init__(*args, **kwargs)
        self.callback = callback
        self.setWindowTitle('Set polling period')
        label = QLabel('Pooling period, minutes:')
        self.line_edit = QLineEdit()
        self.line_edit.editingFinished.connect(self._get_period)
        widget_layout = QHBoxLayout()
        widget_layout.addWidget(label)
        widget_layout.addWidget(self.line_edit)
        widget_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(widget_layout)

    def _get_period(self):
        value = self.line_edit.text()
        try:
            value = float(value)
            self.callback(value)
            self.close()
        except ValueError:
            pass


class Application(QApplication):
    LOG_DIRECTORY = 'logs'
    FIELD_NAMES = ('oil', 'emulsion', 'water')

    # Путь до лог-файла
    file_path = None
    # Период опроса, мс
    pooling_period = 60 * 1e3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_logger()
        self.pooling_period_selector = PoolingPeriodSelector(callback=self._set_pooling_period)
        self.main_window = MainWindow()
        self.main_window.add_menubar_action('Connect to server', self._tcp_client_setup)
        self.main_window.add_menubar_action('Set polling period', self._show_polling_period_selector)
        self.main_window.add_menubar_action('Save chart', self._handle_image_save)

    def _setup_logger(self):
        """Инициализация файла лога текущего эксперимента"""
        if not os.path.exists(self.LOG_DIRECTORY):
            os.mkdir(self.LOG_DIRECTORY)
        current_date = dt.datetime.now().strftime('%d-%m-%y-%H-%M')
        filename = f'{current_date}_experiment_log.csv'
        self.file_path = os.path.join(self.LOG_DIRECTORY, filename)
        log_file = open(self.file_path, 'w')
        log_file.close()

    def _handle_log_write(self, values: dict):
        with open(self.file_path, 'a+', newline='') as log_file:
            writer = csv.DictWriter(log_file, fieldnames=self.FIELD_NAMES)
            writer.writerow(values)

    def _tcp_client_setup(self):
        """Инициализация TCP-клиента"""
        self._tcp_client = Client('localhost', 80, int(self.pooling_period * 1e-3))
        self._tcp_client_timer = QTimer()
        self._tcp_client_timer.setInterval(self.call_period)
        self._tcp_client_timer.timeout.connect(self._handle_tcp_client_request)
        self._tcp_client_timer.start()

    def _handle_tcp_client_request(self):
        """Обработчик TCP-клиента"""
        try:
            image, mask, time_step, values = self._tcp_client.receive()
            self._handle_log_write(values)
            self.main_window.central_widget.chart.add_new_values(time_step, values)
            self.main_window.central_widget.set_text(values)
            self.main_window.central_widget.img.draw(image)
            self.main_window.central_widget.segmented_img.draw(mask)
            self.main_window.status_bar.showMessage('Server is connected')
        except ConnectionRefusedError:
            self._tcp_client_timer.stop()
            self.main_window.status_bar.showMessage('Server is disconnected')

    def _show_polling_period_selector(self):
        self.pooling_period_selector.show()

    def _set_pooling_period(self, period):
        self.pooling_period = int(period * 1e3)
        self._tcp_client.update_timestep(period)

    def _handle_image_save(self):
        filename = QFileDialog.getSaveFileName(None, 'Open File', './', "Image (*.png *.jpg *jpeg)")[0]

        with open(self.file_path, 'r') as log_file:
            reader = csv.DictReader(log_file, fieldnames=self.FIELD_NAMES)
            data_to_plot = {name: [] for name in self.FIELD_NAMES}
            for row in reader:
                for key, value in row.items():
                    data_to_plot[key].append(value)

        fig, ax = plt.subplots(1)
        for key, value in data_to_plot.items():
            ax.plot(value, label=key)
        ax.set_xlabel('Time, minutes')
        ax.set_ylabel('Fraction, %')
        ax.grid(True)
        ax.legend()

        fig.savefig(filename)


app = Application(sys.argv)
sys.exit(app.exec_())
