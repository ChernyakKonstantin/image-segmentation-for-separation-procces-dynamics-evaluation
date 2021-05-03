# TODO Хочу, чтобы двойным кликом по окошку всплывало окно в большем размере, которое также уходило по двойному клику.
# TODO Пусть оно прям на фото выделяет
import sys

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QWindow
from PyQt5.QtWidgets import QActionGroup, QApplication, QGridLayout, QLabel, QMainWindow, QMenu, QPushButton, QWidget


class InteractiveMaskDisplay(QWidget):
    """Класс отображения изображения"""

    @staticmethod
    def _get_default_pixmap():
        """Метод загрузки изображения по умолчанию"""
        q_image = QImage()
        q_image.load('blank.png')
        return QPixmap.fromImage(q_image)

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._setup_image()
        self._setup_menu_pbtn()
        self._setup_layout()

    def _setup_image(self):
        self._img = QLabel()
        self._img.setPixmap(InteractiveMaskDisplay._get_default_pixmap())

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

    def _setup_layout(self):
        widget_layout = QGridLayout()
        widget_layout.addWidget(self._img, 0, 0, Qt.AlignLeft)
        widget_layout.addWidget(self.menu_pbtn, 1, 0, Qt.AlignLeft)
        self.setLayout(widget_layout)

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

    def draw(self, img: np.ndarray):
        """Метод отрисовки изображения"""
        h, w, c = img.shape
        q_image = QImage(bytes(img), w, h, c * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self._img.setPixmap(pixmap)

    # Нельзя переименовать с нижним подчеркиванием
    def mouseDoubleClickEvent(self, event):
        """Обработчик двойного клика"""
        self.increased_window = QWindow()
        self.increased_window.setTitle('Segmentation')
        self.increased_window.show()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(InteractiveMaskDisplay('Urod'))
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
