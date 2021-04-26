# TODO Добавить темную тему
# TODO Добавить печать тренда

import socket
import sys
import time
from threading import Thread

import cv2 as cv
import numpy as np
from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtGui import QColor, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget

from interactive_chart import BaseTimeSeries
from interactive_mask_display import InteractiveMaskDisplay


class Client:
    """Класс TCP-клиента, опрашивающего сервер для получения результатов сегментации."""
    def __init__(self, ip: str, port: int):
        self._address = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(self._address)

    def receive(self):
        raise NotImplementedError  # received = str(self._sock.recv(1024), "utf-8")


class LabeledCanvas(QWidget): #TODO чтобы часто не обрашаться сделать изменение хранимое значенияр азмера окна по событию изменение размера
    # Класс для отрисовки изображений
    # empty_image = QImage(np.zeros([1280, 720, 3], dtype='uint8'), 100, 100, QImage.Format_RGB888)  # Not fully correct

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QColor(130, 120, 190))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        self.label = QLabel(self)
        self.label.setFixedHeight(20)
        self.label.setText(title)

        self.image = QLabel(self)
        self.image.setMinimumSize(QSize(432, 240))
        # self.image.setMaximumSize(QSize(864, 480))
        # self.image.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.image.setSizeIncrement(16, 9)
        # self.image.setPixmap(QPixmap.fromImage(LabeledCanvas.empty_image))

        layout = QVBoxLayout()
        # layout.setAlignment(Qt.AlignCenter)  # layout.setAlignment(self.image, Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.addWidget(self.image)
        # layout.addStretch()

        self.setLayout(layout)

        # self.image.setScaledContents(True)

    def draw(self, image: np.ndarray):
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        canvas_size = self.image.size()
        target_shape = canvas_size.width(), canvas_size.height()
        # resized_image = cv.resize(rgb_image, target_shape)
        q_image = QImage(rgb_image, rgb_image.shape[1], rgb_image.shape[0], 3 * rgb_image.shape[1], QImage.Format_RGB888)  # Not fully correct
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(canvas_size, Qt.KeepAspectRatio)

        self.image.setPixmap(scaled_pixmap)  # pixmap


class CentralWidget(QWidget):
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

        self.show()  #self.showFullScreen()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = MainWindow()

    def process_image(self):
        """Реализовать создание снимка, его обработку и вывод снимка, маски, графика"""





app = Application(sys.argv)  # what's sys.argv?
sys.exit(app.exec_())