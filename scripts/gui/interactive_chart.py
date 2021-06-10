import datetime
import sys
from typing import Tuple

from PyQt5.QtChart import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QApplication, QCalendarWidget, QCheckBox, QFileDialog, QLabel, QMainWindow, QTimeEdit, \
    QWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout


class TimeSeriesChart(QWidget):
    def __init__(self, *args, **kwargs):
        super(TimeSeriesChart, self).__init__()
        self.start_date = datetime.datetime.now()
        self.end_date = datetime.datetime.now() + datetime.timedelta(seconds=5)

        self.chart = BaseTimeSeries(*args, **kwargs)

        self.calendar_start_date = QCalendarWidget()
        self.calendar_start_date.setGridVisible(True)
        self.calendar_end_date = QCalendarWidget()
        self.calendar_end_date.setGridVisible(True)

        self.start_time_selector = QTimeEdit()
        self.end_time_selector = QTimeEdit()
        self.time_selector_label = QLabel('Set period')
        self.time_selector_checkbox = QCheckBox()
        self.time_selector_checkbox.stateChanged.connect(self._set_time_period)

        time_selector_layout = QHBoxLayout()
        time_selector_layout.addWidget(self.start_time_selector)
        time_selector_layout.addWidget(self.end_time_selector)
        time_selector_layout.addWidget(self.time_selector_label)
        time_selector_layout.addWidget(self.time_selector_checkbox)
        time_selector_layout.setAlignment(Qt.AlignLeft)

        widget_layout = QVBoxLayout()
        widget_layout.addWidget(self.chart)
        widget_layout.addLayout(time_selector_layout)
        self.setLayout(widget_layout)

    def _on_start_date_clicked(self):
        self.calendar_start_date.show()

    def _on_end_date_clicked(self):
        self.calendar_end_date.show()

    def _set_start_date(self):
        self.start_date = self.calendar_start_date.selectedDate()
        print(self.start_date)

    def _set_end_date(self):
        self.end_date = self.calendar_end_date.selectedDate()

    def add_new_values(self, *args, **kwargs):
        """Wrapper"""
        self.chart.add_new_values(*args, **kwargs)

    def _on_save_btn_clicked(self):
        self.chart.save_as_image()

    def _set_time_period(self):
        if self.time_selector_checkbox.isChecked():
            self.chart.set_manual_period(True)
            start_time = self.start_time_selector.time().toPyTime()
            end_time = self.end_time_selector.time().toPyTime()
            self.chart.set_period(start_time, end_time)
        else:
            self.chart.set_manual_period(False)


class BaseTimeSeries(QChartView):
    """Базовый класс графика временных рядов"""

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self._manual_period = False

        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat('hh:mm:ss')
        self.x_axis.setRange(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(seconds=5))
        self.x_axis.setTitleText('Time')

        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 100)
        self.y_axis.setTitleText('Fraction, %')

        self.oil_series = QLineSeries(name='Oil fraction')
        self.emulsion_series = QLineSeries(name='Emulsion fraction')
        self.water_series = QLineSeries(name='Water fraction')

        self.chart = QChart()
        self.chart.setTitle('Fraction ratio')
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
        self.setRubberBand(QChartView.HorizontalRubberBand)

    def _update_time_axis(self, new_limit: datetime.datetime):
        """
        Метод обновления границ временного ряда.

        """
        if not self.manual_period:
            self.x_axis.setMin(new_limit - datetime.timedelta(minutes=1))
            self.x_axis.setMax(new_limit)

    def _update_series(self, values: Tuple[float, float, float]):
        """
        Метод добавления новых значений временных рядов.

        """
        oil_value, emulsion_value, water_value = values
        self.oil_series.append(QPointF(self.x_axis.max().toMSecsSinceEpoch(), oil_value))
        self.emulsion_series.append(QPointF(self.x_axis.max().toMSecsSinceEpoch(), emulsion_value))
        self.water_series.append(QPointF(self.x_axis.max().toMSecsSinceEpoch(), water_value))

    def add_new_values(self, data: Tuple[datetime.datetime, Tuple[float, float, float]]):
        """
        Метод добавления новых значений временных рядов и момента времени.

        """
        datetime, values = data
        self._update_time_axis(datetime)
        self._update_series(values)

    def save_as_image(self):
        try:
            image = self.grab()
            filename = QFileDialog.getSaveFileName(None, 'Open File', './', "Image (*.png *.jpg *jpeg)")[0]
            image.save(filename)
        except:
            pass

    def set_manual_period(self, state: bool):
        self.manual_period = state

    def set_period(self, start_time, end_time):
        self.x_axis.setMin(start_time)
        self.x_axis.setMax(end_time)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(TimeSeriesChart())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
