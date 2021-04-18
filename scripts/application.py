from os import path

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
