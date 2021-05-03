import datetime
import sys
from typing import Tuple, Any

from PyQt5.QtChart import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow


class BaseTimeSeries(QChartView):
    """Базовый класс графика временных рядов"""

    def __init__(self,
                 title: str = '',
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat('hh:mm:ss')
        self.x_axis.setRange(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(minutes=1))
        self.x_axis.setTitleText('Time')

        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 100)
        self.y_axis.setTitleText('Fraction, %')

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

    def _update_time_axis_max(self, new_limit: datetime.datetime):
        """
        Метод обновления правой границы временного ряда.

        """
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
        self._update_time_axis_max(datetime)
        self._update_series(values)

    def demo_func(self, some_parameter: Any):
        """Метод, который должен быть вызван внешним обработчиком."""
        print('I was called!')


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(BaseTimeSeries())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
