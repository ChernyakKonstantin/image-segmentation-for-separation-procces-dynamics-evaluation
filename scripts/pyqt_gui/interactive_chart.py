from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar, \
    QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QEvent, QThread, QThreadPool, Qt, QSize, QPointF, QRectF, QMargins, Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QWheelEvent, QMouseEvent
from PyQt5.QtChart import QChart, QLineSeries, QChartView, QAbstractAxis, QValueAxis, QLegend
import sys
import cv2 as cv
import numpy as np
import datetime as dt


class InteractiveChart(QChartView):
    """
    Скроллинг колесиком мыши - зумминг. (Done)
    Нажатием левой кнопки мыши - перемещение. (Done)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enable_move = False

        self.series = QLineSeries()

        h_axis = QValueAxis() # change to Datetime
        h_axis.setRange(0, 100)
        h_axis.setTitleText('Time')

        v_axis = QValueAxis()
        v_axis.setRange(0, 100)
        v_axis.setTitleText('Fraction, %')

        self.chart = QChart()
        self.chart.setTitle('Fraction ratio')
        self.chart.addAxis(h_axis, Qt.AlignBottom)
        self.chart.addAxis(v_axis, Qt.AlignLeft)
        self.chart.addSeries(self.series)

        self.series.attachAxis(h_axis)
        self.series.attachAxis(v_axis)

        self.setChart(self.chart)

        self.setup_pseudo_data_gen_timer()


    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.chart.zoomReset()
        elif event.button() == Qt.LeftButton:
            self.enable_move = True
            self.cursor_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.enable_move = False

    def mouseMoveEvent(self, event):
        if self.enable_move:
            d = event.pos() - self.cursor_pos
            self.cursor_pos = event.pos()
            dx = -d.x()
            dy = d.y()
            self.chart.scroll(dx, dy)

    def wheelEvent(self, event):
        delta = event.angleDelta()
        if delta.y() > 0:
            self.chart.zoomIn()
        elif delta.y() < 0:
            self.chart.zoomOut()

    def pseudo_data_gen(self):
        x = np.random.random() * 100
        y = np.random.random() * 100
        self.series.append(QPointF(x, y))
        self.pseudo_data_gen_timer.start()

    def setup_pseudo_data_gen_timer(self):
        self.pseudo_data_gen_timer = QTimer()
        self.pseudo_data_gen_timer.setInterval(300)
        self.pseudo_data_gen_timer.timeout.connect(self.pseudo_data_gen)
        self.pseudo_data_gen_timer.start()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(InteractiveChart())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)  # what's sys.argv?
    sys.exit(app.exec_())
