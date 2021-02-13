import csv
import tkinter as tk
from queue import Queue
from threading import Thread
from time import time
from tkinter import ttk

import cv2 as cv
from PIL import Image, ImageTk

import constants
import widgets as w


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

    def camera_setup(self):
        """Функция инизиализации и настройки экзмепляра класса cv2.VideoCapture

        Returns:
            capture(cv2.VideoCapture): Настроенный экземпляр класса cv2.VideoCapture

        """
        self.capture = cv.VideoCapture(constants.DEVICE_ID, cv.CAP_ANY)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, constants.CAMERA_RESOLUTION[0])
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, constants.CAMERA_RESOLUTION[1])

    def run_camera(self):
        self.camera_thread = CameraThread(
            self.queue,
            self.capture,
            constants.PERIOD,
            self.mf.image.get_canvas_size()
        )
        self.camera_thread.start()

    def check_queue(self):
        if not self.queue.empty():
            self.image = self.queue.get()
            self.mf.image.create_image(0, 0, anchor='nw', image=self.image)
        self.after(1, self.check_queue)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('1280x720')
        self.resizable(False, False)

        self.title('Separation Dynamics')

        self.mf = w.MainFrame(self)
        self.mf.grid(sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.queue = Queue()
        self.camera_setup()

        self.run_camera()

        self.after(100, self.check_queue)


class CameraThread(Thread):
    """Поток для считывания изображения с камеры."""

    def __init__(self, queue, capture, period, image_size, *args, **kwargs):
        """

        Args:
            queue (queue.Queue):
            capture (cv2.VideoCapture):
            period (float): Период считвания с камеры (в секундах)
        """
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.capture = capture
        self.period = period
        self.image_width, self.image_height = image_size
        print(self.image_width, self.image_height)

    def run(self):
        t_1 = time()
        while True:
            if time() - t_1 >= self.period:
                _, image = self.capture.read()
                image = cv.resize(image, (self.image_width, self.image_height))
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                self.queue.put(image)
                t_1 = time()


if __name__ == '__main__':
    app = Application()
    app.mainloop()
