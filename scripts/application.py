import csv
from os import remove
from os.path import join
from time import time

import cv2 as cv
import numpy as np
import tensorflow as tf

import constants
from commons import make_dir

import tkinter as tk

def create_mask(pred):
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


def predict(image, model):
    """Функция предсказания маски изображения.

    Args:
        image (numpy.ndarray): Изображение, для которого необходимо предсказать маску
        model (tensorflow.function): Модель для предсказания маски

    Returns:
        mask (numpy.ndarray): Одноканальное изображение маски

    """
    image = np.expand_dims(image, axis=0)
    image = image.astype('float32')
    pred = model(image)
    mask = create_mask(pred)
    return mask


def calc_fractions(mask):
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


def get_capture():
    """Функция инизиализации и настройки экзмепляра класса cv2.VideoCapture

    Returns:
        capture(cv2.VideoCapture): Настроенный экземпляр класса cv2.VideoCapture

    """
    capture = cv.VideoCapture(constants.DEVICE_ID, cv.CAP_ANY)
    capture.set(cv.CAP_PROP_FRAME_WIDTH, constants.CAMERA_RESOLUTION[0])
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, constants.CAMERA_RESOLUTION[1])
    return capture


def write_csv(file_path, data):
    """Функция записи данных в конец csv файла.

    Args:
        file_path (str): Путь до файла записи данных
        data (tuple): Записываемые данные

    """
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def run_app():
    """Функция запуска приложения.

    Функция выполняет следующие задачи:
    1. Делает снимок с камеры;
    2. Использует модель для предсказания семантической маски изображения;
    3. Вычисляет доли фракций;
    4. Логирует данные о долях фракций в файл.
    5. Выводит изображения снимка и соответствующей маски.

    Период срабатывания приложения определяется в файле constants.


    """
    log_dir = join(
        constants.PROJECT_DIRNAME,
        constants.LOG_DIR,
    )
    make_dir(log_dir)

    log_file_path = join(
        log_dir,
        constants.LOG_FILENAME
    )
    remove(log_file_path)  # Удаление старого файла лога

    model_dir = join(constants.PROJECT_DIRNAME, constants.MODEL_DIR)
    model = tf.saved_model.load(model_dir)

    cap = get_capture()

    timer = 0
    while True:
        if time() - timer >= constants.PERIOD:
            ret, image = cap.read()

            mask = predict(image, model)

            oil_fraction, emulsion_fraction, water_fraction = calc_fractions(mask)
            write_csv(log_file_path, (oil_fraction, emulsion_fraction, water_fraction))

            cv.imshow('Segmented Image', cv.resize(mask, (300, 300)))
            cv.imshow('Image', cv.resize(image, (300, 300)))

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            timer = time()


class Application(tk.Tk):
    """Класс оконного приложения

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Separation Dynamics')
        self.


if __name__ == '__main__':
    run_app()



