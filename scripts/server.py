"""Модуль сервера, запускаемый на ПК, выполняющем сегментацию изображений."""

import struct
from os import path
from socketserver import BaseRequestHandler, TCPServer
from typing import Tuple

import cv2 as cv
import numpy as np
import tensorflow as tf

import constants


class ImageProcessor:

    @staticmethod
    def _create_mask(pred):
        """Функция создания изображения маски.

        Args:
            pred (tensorflow.Tensor: Предсказанная моделью маска

        Returns:
            mask (numpy.ndarray): Одноканальное изображение маски

        """
        mask = tf.argmax(pred, axis=-1)[0]
        mask = mask.numpy()
        mask = mask.astype('uint8')
        return mask

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
        image = np.expand_dims(image, axis=0)
        image = image.astype('float32')
        pred = self.model(image)
        return pred


    def process_frame(self):
        ret, image = self.capture.read()
        pred = self._predict(image)
        mask = ImageProcessor._create_mask(pred)
        oil_fraction, emulsion_fraction, water_fraction = ImageProcessor._calc_fractions(mask)
        return mask, (oil_fraction, emulsion_fraction, water_fraction)


class JetsonServerHandler(BaseRequestHandler):
    """Класс обработчика запросов.
    Возвращает результат сегментации: кортеж из изображения маски фракций и кортежа долей их площадей.
    """
    def __init__(self, *args, **kwargs):
        super(JetsonServerHandler, self).__init__(*args, **kwargs)
        self._image_processor = ImageProcessor()

    def handle(self):
        mask: np.ndarray
        ratio: Tuple[float, float, float]
        byte_mask: bytes
        byte_ratio: bytes

        mask, ratio = self._image_processor.process_frame()
        # TODO найти способ объединить эти элементы для совместной отправки
        byte_mask = mask.tobytes()
        byte_ratio = struct.pack('3f', *ratio)

        self.request.sendall(byte_ratio)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 80

    with TCPServer((HOST, PORT), JetsonServerHandler) as server:
        print(f'Server started on {HOST}, port {PORT}')
        server.serve_forever()
