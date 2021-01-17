from os import mkdir
from os.path import exists

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.metrics import MeanIoU


def make_dir(path):
    """Функция создания указанной директории.

    Args:
        path: Путь до директории

    """
    if not exists(path):
        mkdir(path)


class UpdatedMeanIoU(MeanIoU):
    """Класс tensorflow.keras.metrics.MeanIoU с исправлениями.

     https://github.com/tensorflow/tensorflow/issues/32875

     """
    def __init__(self,
                 y_true=None,
                 y_pred=None,
                 num_classes=None,
                 name=None,
                 dtype=None):
      super(UpdatedMeanIoU, self).__init__(num_classes = num_classes,name=name, dtype=dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.math.argmax(y_pred, axis=-1)
        return super().update_state(y_true, y_pred, sample_weight)

def fig2rgb_array(fig):
    """Функция перевода matplotlib.pyplot.figure в numpy.ndarray.

    Args:
      fig (matplotlib.pyplot.figure): График после построения средствами matplotlib

    Returns:
      (numpy.ndarray): График в формате numpy, готовый к отрисовке

    """
    fig.canvas.draw()
    buf = fig.canvas.tostring_rgb()
    ncols, nrows = fig.canvas.get_width_height()
    return np.fromstring(buf, dtype=np.uint8).reshape(nrows, ncols, 3)


def plot_img(fractions):
    """Фукнция построения графика в формате изображения.п

    Функция строит график по последним 50 значениям.

    Args:
        fractions (tuple): Кортеж данных о долях фракций

    Returns:
        (numpy.ndarray): Изображение графика


  """
    fig, ax = plt.subplots()
    for fraction in fractions:
        ax.plot(fraction[-50:])
    return fig2rgb_array(fig)
