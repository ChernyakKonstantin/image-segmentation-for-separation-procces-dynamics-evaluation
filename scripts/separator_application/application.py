import csv
import tkinter as tk
from queue import Queue
from threading import Thread
from time import time, sleep

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
        self.write_to_status_panel('Capture is ready')

    def model_setup(self):
        sleep(15)
        self.write_to_status_panel('Model is ready')

    def run_camera(self):
        self.camera_thread = CameraThread(
            self.queue,
            self.capture,
            constants.PERIOD,
            self.mainframe.image.get_canvas_size()
        )
        self.camera_thread.start()
        self.write_to_status_panel('Camera thread is ready')

    def check_queue(self):
        if not self.queue.empty():
            self.image = self.queue.get()
            self.mainframe.image.create_image(0, 0, anchor='nw', image=self.image)
        self.write_to_status_panel('Updated')
        self.after(1, self.check_queue)

    def write_to_status_panel(self, text):
        self.mainframe.info.write_new_line(text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry('1280x720')
        self.resizable(False, False)

        self.title('Separation Dynamics')

        self.mainframe = w.MainFrame(self)
        self.mainframe.grid(sticky=tk.NSEW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.update_idletasks()

        self.queue = Queue()

        self.camera_setup()

        self.run_camera()

        # self.model_setup()

        self.check_queue()



if __name__ == '__main__':
    app = Application()
    app.mainloop()

