# TODO Хочу, чтобы двойным кликом по окошку всплывало окно в большем размере, которое также уходило по двойному клику.

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar, \
    QGridLayout, QSizePolicy, QRadioButton, QCheckBox, QButtonGroup, QGroupBox, QCheckBox
from PyQt5.QtCore import QTimer, QEvent, QThread, QThreadPool, Qt, QSize, QPointF, QRectF, QMargins, Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QWheelEvent, QMouseEvent
from PyQt5.QtChart import QChart, QLineSeries, QChartView, QAbstractAxis, QValueAxis, QLegend
import sys
import cv2 as cv
import numpy as np
import datetime as dt


# IMAGE SIZE 640 x 360

class InteractiveMaskDisplay(QWidget):

    @staticmethod
    def _get_default_pixmap():
        q_image = QImage()
        q_image.load(r'C:\Users\zvfrf\Documents\PyCharmProjects\diploma_prj\blank.png')
        return QPixmap.fromImage(q_image)

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._setup_buttons()
        self._setup_btn_group()
        self._setup_image()
        self._setup_layout()

    def _setup_buttons(self):
        self.show_all_cbtn = QCheckBox('Show all layers')
        self.show_all_cbtn.clicked.connect(self._on_show_all_cbtn_clicked)

        self.show_oil_layer_cbtn = QCheckBox('Show oil layer')
        self.show_oil_layer_cbtn.clicked.connect(self._on_cbtn_clicked)

        self.show_emulsion_cbtn = QCheckBox('Show emulsion layer')
        self.show_emulsion_cbtn.clicked.connect(self._on_cbtn_clicked)

        self.show_water_cbtn = QCheckBox('Show water layer')
        self.show_water_cbtn.clicked.connect(self._on_cbtn_clicked)

    def _setup_btn_group(self):
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        self.button_group.addButton(self.show_oil_layer_cbtn)
        self.button_group.addButton(self.show_emulsion_cbtn)
        self.button_group.addButton(self.show_water_cbtn)

    def _setup_image(self):
        self.img = QLabel()
        self.img.setPixmap(InteractiveMaskDisplay._get_default_pixmap())

    def _setup_layout(self):
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.show_all_cbtn)
        btn_layout.addWidget(self.show_oil_layer_cbtn)
        btn_layout.addWidget(self.show_emulsion_cbtn)
        btn_layout.addWidget(self.show_water_cbtn)

        widget_layout = QGridLayout()
        widget_layout.addLayout(btn_layout, 0, 0, Qt.AlignLeft)
        widget_layout.addWidget(self.img, 0, 1, Qt.AlignLeft)
        self.setLayout(widget_layout)

    def _on_show_all_cbtn_clicked(self):
        if self.show_all_cbtn.isChecked():
            self.show_oil_layer_cbtn.setCheckState(Qt.Checked)
            self.show_emulsion_cbtn.setCheckState(Qt.Checked)
            self.show_water_cbtn.setCheckState(Qt.Checked)
        else:
            self.show_oil_layer_cbtn.setCheckState(Qt.Unchecked)
            self.show_emulsion_cbtn.setCheckState(Qt.Unchecked)
            self.show_water_cbtn.setCheckState(Qt.Unchecked)

    def _on_cbtn_clicked(self):
        if all([button.isChecked() for button in self.button_group.buttons()]):
            self.show_all_cbtn.setCheckState(Qt.Checked)
        else:
            self.show_all_cbtn.setCheckState(Qt.Unchecked)


    def draw(self, image: np.ndarray):
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        q_image = QImage(rgb_image, rgb_image.shape[1], rgb_image.shape[0], 3 * rgb_image.shape[1],
                         QImage.Format_RGB888)  # Not fully correct
        pixmap = QPixmap.fromImage(q_image)
        self.image.setPixmap(pixmap)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(InteractiveMaskDisplay('Urod'))
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)  # what's sys.argv?
    sys.exit(app.exec_())
