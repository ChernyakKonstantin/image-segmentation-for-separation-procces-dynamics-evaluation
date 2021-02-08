import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2 as cv
# import numpy as np
from threading import Thread


from threading import Thread
from time import sleep
import tkinter as tk
from queue import Queue

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
    capture = cv.VideoCapture(constants.DEVICE_ID, cv.CAP_DSHOW)
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




class LabelCanvas(ttk.Frame):

    def __init__(self, parent, title, canvas_width, canvas_height, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = ttk.Label(self, anchor=tk.CENTER, text=title)
        self.canvas = tk.Canvas(self, bg='blue', width=canvas_width, height=canvas_height)

        self.title.grid(row=0, sticky=tk.EW)
        self.canvas.grid(row=1, sticky=tk.NSEW)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def create_image(self, *args, **kwargs):
        self.canvas.create_image(*args, **kwargs)


class LabelsPanel(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.oil_fraction = tk.StringVar()
        self.emulsion_fraction = tk.StringVar()
        self.water_fraction = tk.StringVar()

        self.oil_fraction.set('Oil: None%')
        self.emulsion_fraction.set('Emulsion: None%')
        self.water_fraction.set('Water: None%')

        super().__init__(parent, *args, **kwargs)
        ttk.Label(self, textvariable=self.oil_fraction, anchor=tk.W).grid(row=0, sticky=tk.EW)
        ttk.Label(self, textvariable=self.emulsion_fraction, anchor=tk.W).grid(row=1, sticky=tk.EW)
        ttk.Label(self, textvariable=self.water_fraction, anchor=tk.W).grid(row=2, sticky=tk.EW)


class MainFrame(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pic = None
        self.queue = Queue()
        self.cap = get_capture()

        self.image = LabelCanvas(self, 'Original', canvas_width=400, canvas_height=300)
        self.mask = LabelCanvas(self, 'Segmented', canvas_width=400, canvas_height=300)
        self.plot = LabelCanvas(self, 'Trend', canvas_width=800, canvas_height=600)

        self.status_info = ttk.Entry(self)
        # self.data = LabelsPanel(self)



        # img = Image.open("image.jpg")
        # img = img.resize((100, 100))
        # self.img = ImageTk.PhotoImage(img)
        # self.img = gen_img()
        # self.image.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.image.grid(row=0, column=0)
        self.mask.grid(row=1, column=0)
        self.plot.grid(row=0, column=1, rowspan=2)

        self.status_info.grid(row=2, column=0, columnspan=2)
        # self.data.grid(row=0, column=3)
        # self.grid_columnconfigure(1, weight=1)

        self.after(100, self.go)

    def go(self):
        p = Backend(self.queue, self.cap)
        p.start()
        self.after(15, self.check_queue)

    def check_queue(self):
        if not self.queue.empty():
            self.pic = self.queue.get()
            self.image.create_image(0, 0, anchor=tk.NW, image=self.pic)
            # self.after(0, self.go)
            print('Upd')
        self.after(15, self.go)
        # print('Upd')


    def grid(self, sticky=tk.NSEW, **kwargs):
        super().grid(sticky=sticky, **kwargs)


class Backend(Thread):

    def __init__(self, queue, cap, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap = cap
        self.queue = queue

    def run(self):
        ret, image = self.cap.read()
        image = cv.resize(image, (360,180))
        img = ImageTk.PhotoImage(Image.fromarray(image))
        self.queue.put(img)



def gen_img():
    """I made it just to test."""
    img = np.random.randint(low=0, high=255, size=(300, 300, 3), dtype='uint8')
    return ImageTk.PhotoImage(Image.fromarray(img))



if __name__ == '__main__':
    BACKGROUND_COLOR = '#282d2f'
    TEXT_COLOR = '#d4d5d5'


    root = tk.Tk()
    root.title('Separation Dynamics')
    # root.attributes("-fullscreen", True)
    style = ttk.Style()
    style.configure(
        'TFrame',
        background=BACKGROUND_COLOR,
        # borderwidth=5
    )
    style.configure(
        'TLabel',
        background=BACKGROUND_COLOR,
        foreground=TEXT_COLOR,
        relief='flat',
        font=('TkDefaultFont', 12),
    )

    # root.geometry('1280x720')
    # root.resizable(False, False)

    a = MainFrame(root)
    a.grid()
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.mainloop()