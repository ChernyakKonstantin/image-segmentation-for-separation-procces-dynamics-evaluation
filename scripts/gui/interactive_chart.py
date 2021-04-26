# TODO Добавить адекватную легенду и недостающие Series.
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar, \
    QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QEvent, QThread, QThreadPool, Qt, QSize, QPointF, QRectF, QMargins, Qt, QDateTime
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
                 y_label: str = '',
                 title: str = '',
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat('hh:mm:ss')
        self.x_axis.setRange(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.x_axis.setTitleText(x_label)

        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 100)
        self.y_axis.setTitleText(y_label)

        self.oil_series = QLineSeries()
        self.emulsion_series = QLineSeries()
        self.water_series = QLineSeries()

        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.addAxis(self.x_axis, Qt.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignLeft)
        self.chart.addSeries(self.oil_series)
        self.chart.addSeries(self.emulsion_series)
        self.chart.addSeries(self.water_series)

        self.oil_series.attachAxis(self.x_axis)
        self.oil_series.attachAxis(self.y_axis)
        self.emulsion_series.attachAxis(self.x_axis)
        self.emulsion_series.attachAxis(self.y_axis)
        self.water_series.attachAxis(self.x_axis)
        self.water_series.attachAxis(self.y_axis)

        self.setChart(self.chart)

    def update_time_axis(self, new_limit: datetime.datetime):
        """
        Метод обновления правой границы временного ряда.

        """
        self.x_axis.setRange(self.x_axis.min(), new_limit)

    def update_series(self, values: tuple):
        """
        Метод добавления новых значений временных рядов.

        """
        oil_value, emulsion_value, water_value = values
        self.oil_series.append(oil_value)
        self.emulsion_series.append(emulsion_value)
        self.water_series.append(water_value)



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


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(BaseTimeSeries())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)  # what's sys.argv?
    sys.exit(app.exec_())
