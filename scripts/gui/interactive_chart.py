import sys

from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow


class TimeSeriesChart(QChartView):
    """Базовый класс графика временных рядов"""

    x = 0.0

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.x_axis = QValueAxis()
        self.x_axis.setRange(0, 100)
        self.x_axis.setTitleText('Время, минуты')

        self.y_axis = QValueAxis()
        self.y_axis.setRange(0, 100)
        self.y_axis.setTitleText('Доля фракции, %')

        self.oil_series = QLineSeries(name='Масло')
        self.emulsion_series = QLineSeries(name='Эмульсия')
        self.water_series = QLineSeries(name='Вода')

        self.chart = QChart()
        self.chart.setTitle('Доля фракции')
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

    def _update_time_axis(self, time_step: float):
        """
        Метод обновления границ временного ряда.

        """
        self.x_axis.setRange(self.x_axis.min() + time_step, self.x_axis.max() + time_step)

    def _update_series(self, time_step: float, values: dict):
        """
        Метод добавления новых значений временных рядов.

        """
        self.x = self.x + time_step
        self.oil_series.append(QPointF(self.x, values['oil']))
        self.emulsion_series.append(QPointF(self.x, values['emulsion']))
        self.water_series.append(QPointF(self.x, values['water']))

    def add_new_values(self, time_step: float, values: dict):
        """
        Метод добавления новых значений временных рядов и момента времени.

        """
        self._update_time_axis(time_step)
        self._update_series(time_step, values)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(TimeSeriesChart())
        self.main_window.show()


if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
