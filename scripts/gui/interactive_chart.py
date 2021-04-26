# TODO Добавить адекватную легенду и недостающие Series.
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar, \
    QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QEvent, QThread, QThreadPool, Qt, QSize, QPointF, QRectF, QMargins, Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QWheelEvent, QMouseEvent
from PyQt5.QtChart import QChart, QLineSeries, QChartView, QAbstractAxis, QValueAxis, QLegend, QDateTimeAxis
import sys
import cv2 as cv
import numpy as np
import datetime as dt
from typing import Tuple, List, Any
import datetime


class BaseTimeSeries(QChartView):
    def __init__(self,
                 x_label: str = '',
                 x_range: Tuple[float, float] = (0, 1),
                 y_label: str = '',
                 y_range: Tuple[float, float] = (0, 1),
                 title: str = '',
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        x_axis = QDateTimeAxis()
        x_axis.setFormat('hh:mm:ss')
        x_axis.setRange()  # TODO: Настроить
        x_axis.setTitleText(x_label)

        y_axis = QValueAxis()
        y_axis.setRange(*y_range)
        y_axis.setTitleText(y_label)

        self.series = QLineSeries()

        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.addAxis(x_axis, Qt.AlignBottom)
        self.chart.addAxis(y_axis, Qt.AlignLeft)
        self.chart.addSeries(self.series)

        self.series.attachAxis(x_axis)
        self.series.attachAxis(y_axis)

        self.setChart(self.chart)


class PreviewTimeSeries(BaseTimeSeries):
    """
    Класс виджета, отображающего весь временной ряд. Имеет область выбора
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRubberBand(QChartView.HorizontalRubberBand)  # Выбор области




class AdvancedTimeSeriesChart(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        v_layout = QVBoxLayout()
        v_layout.addWidget(InteractiveChart(x_label='Time',
                                             x_range=(0, 100),
                                             y_label='Fraction, %',
                                             y_range=(0, 100),
                                             title='Title'))
        v_layout.addWidget(PreviewTimeSeries(x_label='x',
                                             x_range=(0, 1),
                                             y_label='y',
                                             y_range=(0, 1),
                                             title='Title'))

        self.setLayout(v_layout)



class InteractiveChart(BaseTimeSeries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_move = False
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

    def wheelEvent(self, event):  # TODO somehow limit zooming in Y-direction in range (0, 100)
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
        self.main_window.setCentralWidget(AdvancedTimeSeriesChart())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)  # what's sys.argv?
    sys.exit(app.exec_())
