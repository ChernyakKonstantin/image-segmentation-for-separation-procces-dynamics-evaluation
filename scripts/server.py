"""Модуль сервера, запускаемый на ПК, выполняющем сегментацию изображений."""

# Конфигурация сессии при работе с GPU
import tensorflow as tf
# Получить список доступных GPU
physical_devices = tf.config.list_physical_devices('GPU')
# Видеопамять используется по мере необходимости
tf.config.experimental.set_memory_growth(physical_devices[0], True)


import pickle
from os import path
from socketserver import BaseRequestHandler, TCPServer
from typing import Tuple

import cv2 as cv
import numpy as np
import tensorflow as tf

import constants


class ImageProcessor:

    @staticmethod
    def _create_mask(prediction: np.ndarray) -> np.ndarray:
        """
        Функция создания маски изображений из предсказания модели.

        Args:
            prediction (np.ndarray): Предсказание модели

        Returns:
            mask (np.ndarray): Маска изображения

        """
        # Выбрать наиболее вероятные классы для пикселей
        mask = np.argmax(prediction, axis=-1)
        # Добавить ось каналов
        mask = np.expand_dims(mask, axis=-1)
        return mask.astype('uint8')

    @staticmethod
    def _calc_fractions(mask):
        """Функция вычисления долей фракции на изображении.

        Args:
            mask (numpy.ndarray): Семантическая маска изображения

        Returns:
            (tuple): Доля фракций масла, эмульсии, воды

        """
        total = mask.sum()
        oil_fraction = round(mask[mask == constants.OIL_ID].sum() / total, 3)
        emulsion_fraction = round(mask[mask == constants.EMULSION_ID].sum() / total, 3)
        water_fraction = round(mask[mask == constants.WATER_ID].sum() / total, 3)
        return oil_fraction, emulsion_fraction, water_fraction

    def __init__(self):
        self._setup_capture()
        self._setup_model()

    def _setup_capture(self):
        """Функция инизиализации и настройки экзмепляра класса cv2.VideoCapture."""
        self.capture = cv.VideoCapture(constants.DEVICE_ID, cv.CAP_ANY)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, constants.CAMERA_RESOLUTION[0])
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, constants.CAMERA_RESOLUTION[1])

    def _setup_model(self):
        model_dir = path.join(constants.PROJECT_DIRNAME, constants.MODEL_DIR)
        self.model = tf.saved_model.load(model_dir)

    def _predict(self, image):
        """Функция предсказания маски изображения.

        Args:
            image (numpy.ndarray): Изображение, для которого необходимо предсказать маску
            model (tensorflow.function): Модель для предсказания маски

        Returns:
            TODO
        """
        img = np.expand_dims(image, axis=0)
        img = img.astype('float32')
        pred = self.model(img)
        return pred


    def mask_to_rgb(self, mask: np.ndarray):
        water_mask = np.zeros_like(mask)
        water_mask[mask == 2] = 255

        emulsion_mask = np.zeros_like(mask)
        emulsion_mask[mask == 1] = 255

        oil_mask = np.zeros_like(mask)
        oil_mask[mask == 0] = 255

        return np.dstack([water_mask, emulsion_mask, oil_mask]).astype('uint8')


    def process_frame(self):
        ret, image = self.capture.read()
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        pred = self._predict(image)
        mask = ImageProcessor._create_mask(pred)
        rgb_mask = self.mask_to_rgb(mask[0])
        rgb_mask = cv.resize(rgb_mask, (640, 360))

        image = cv.resize(image, (640, 360), cv.INTER_NEAREST)
        res = cv.addWeighted(image, 0.91, rgb_mask, 0.09, 0.0)

        oil_fraction, emulsion_fraction, water_fraction = ImageProcessor._calc_fractions(mask)

        values = {'oil': oil_fraction * 100,
                  'emulsion': emulsion_fraction * 100,
                  'water': water_fraction * 100,
                  }

        return res, values


class JetsonServerHandler(BaseRequestHandler):
    """Класс обработчика запросов.
    Возвращает результат сегментации: кортеж из изображения маски фракций и кортежа долей их площадей.
    """
    _image_processor = ImageProcessor()

    def handle(self):
        mask: np.ndarray
        values: Tuple[float, float, float]

        # image, mask, values = self._image_processor.process_frame()
        image, values = self._image_processor.process_frame()

        # package = pickle.dumps((image, mask, values))
        package = pickle.dumps((image, values))
        self.request.sendall(package)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 80

    with TCPServer((HOST, PORT), JetsonServerHandler) as server:
        print(f'Server started on {HOST}, port {PORT}')
        server.serve_forever()
