import csv
import tkinter as tk
from os import remove
from os.path import join
from queue import Queue
from threading import Thread
from time import sleep
from tkinter import ttk

from PIL import Image, ImageTk


import cv2 as cv
import numpy as np
import tensorflow as tf

import constants
import widgets as w
from commons import make_dir


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


class Application(tk.Tk):
    """Класс оконного приложения

    """
    background_color = '#282d2f'
    text_color = '#d4d5d5'

    def log_setup(self):
        self.log_dir = join(
            constants.PROJECT_DIRNAME,
            constants.LOG_DIR,
        )
        make_dir(self.log_dir)

        self.log_file_path = join(
            self.log_dir,
            constants.LOG_FILENAME
        )
        remove(self.log_file_path)  # Удаление старого файла лога

    def camera_setup(self):
        self.cap = get_capture()

    def model_setup(self):
        self.model_dir = join(constants.PROJECT_DIRNAME, constants.MODEL_DIR)
        self.model = tf.saved_model.load(self.model_dir)

    def inference(self):
        ret, image = self.cap.read()
        mask = predict(image, self.model)
        oil_fraction, emulsion_fraction, water_fraction = calc_fractions(mask)
        write_csv(self.log_file_path, (oil_fraction, emulsion_fraction, water_fraction))


    def go(self):
        p = CameraControl(self.queue, self.cap)
        p.start()
        self.after(1, self.check_queue)

    def check_queue(self):
        if not self.queue.empty():
            self.image = self.queue.get()
            self.mf.image.create_image(0, 0, anchor='nw', image=self.image)
            # print('HERE')
        self.after(1, self.check_queue)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.log_setup()
        self.camera_setup()
        # self.model_setup()
        self.queue = Queue()


        self.title('Separation Dynamics')

        self.style = ttk.Style()
        self.style.configure(
            'TFrame',
            background=Application.background_color,

        )
        self.style.configure(
            'TLabel',
            background=Application.background_color,
            foreground=Application.text_color,
            font=('TkDefaultFont', 12),
        )

        self.mf = w.MainFrame(self)
        self.mf.grid(sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.after(100, self.go)


class CameraControl(Thread):

    def __init__(self, queue, capture, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.capture = capture

    def run(self):
        while True:
            ret, image = self.capture.read()
            image = cv.resize(image, (300, 300))
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            self.queue.put(image)



if __name__ == '__main__':
    app = Application()
    app.mainloop()
