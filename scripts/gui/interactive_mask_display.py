import sys

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QWidget


class InteractiveMaskDisplay(QWidget):
    """Класс отображения изображения"""

    @staticmethod
    def _get_default_pixmap():
        """Метод загрузки изображения по умолчанию"""
        q_image = QImage()
        q_image.load('blank.png')
        return QPixmap.fromImage(q_image)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._setup_image()
        # self._setup_menu_pbtn()
        self._setup_layout()

    def _setup_image(self):
        self._img = QLabel()
        self._img.setPixmap(InteractiveMaskDisplay._get_default_pixmap())

    def _setup_layout(self):
        widget_layout = QGridLayout()
        widget_layout.addWidget(self._img, 0, 0, Qt.AlignLeft)
        widget_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(widget_layout)

    def draw(self, img: np.ndarray):
        """Метод отрисовки изображения"""
        h, w, c = img.shape
        q_image = QImage(bytes(img), w, h, c * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self._img.setPixmap(pixmap)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(InteractiveMaskDisplay())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
