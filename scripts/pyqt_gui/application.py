from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar, QGridLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QEvent, QThread, QThreadPool, Qt, QSize, QPointF
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtChart import QChart, QLineSeries, QChartView
import sys
import cv2 as cv
import numpy as np
import time
from threading import Thread
from queue import Queue
from interactive_chart import InteractiveChart


class LabeledCanvas(QWidget): #TODO чтобы часто не обрашаться сделать изменение хранимое значенияр азмера окна по событию изменение размера
    # Класс для отрисовки изображений
    # empty_image = QImage(np.zeros([1280, 720, 3], dtype='uint8'), 100, 100, QImage.Format_RGB888)  # Not fully correct

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QColor(130, 120, 190))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        self.label = QLabel(self)
        self.label.setFixedHeight(20)
        self.label.setText(title)

        self.image = QLabel(self)
        self.image.setMinimumSize(QSize(432, 240))
        # self.image.setMaximumSize(QSize(864, 480))
        # self.image.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.image.setSizeIncrement(16, 9)
        # self.image.setPixmap(QPixmap.fromImage(LabeledCanvas.empty_image))

        layout = QVBoxLayout()
        # layout.setAlignment(Qt.AlignCenter)  # layout.setAlignment(self.image, Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.addWidget(self.image)
        # layout.addStretch()

        self.setLayout(layout)

        # self.image.setScaledContents(True)

    def draw(self, image: np.ndarray):
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        canvas_size = self.image.size()
        target_shape = canvas_size.width(), canvas_size.height()
        # resized_image = cv.resize(rgb_image, target_shape)
        q_image = QImage(rgb_image, rgb_image.shape[1], rgb_image.shape[0], 3 * rgb_image.shape[1], QImage.Format_RGB888)  # Not fully correct
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(canvas_size, Qt.KeepAspectRatio)

        self.image.setPixmap(scaled_pixmap)  # pixmap


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.webcam_img = LabeledCanvas('Image')
        self.segmented_img = LabeledCanvas('Segmentation')
        self.chart = InteractiveChart()

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.webcam_img)
        v_layout.addWidget(self.segmented_img)

        h_layout = QHBoxLayout()
        # h_layout.setAlignment(Qt.AlignCenter)
        h_layout.addLayout(v_layout)
        h_layout.addWidget(self.chart)

        self.setLayout(h_layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        self.setWindowTitle('Separator Dynamics Estimator')

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        self.menu_bar.addAction('Quit', self.close)

        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)

        self.showFullScreen()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.async_model_setup
        self.camera_setup()  # self.async_camera_setup()
        self.main_window = MainWindow()

        self.run_camera()

    # def async_camera_setup(self):
    #     """Выполняет подготовку видеокамеры в фоновом режиме."""
    #     def camera_setup(parent): # Вопрос, насколько это корректно?
    #         parent.video_cap = cv.VideoCapture(0)
    #         parent.video_cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    #         parent.video_cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
    #         parent.camera_timer = QTimer()
    #         parent.camera_timer.timeout.connect(parent.run_camera)
    #
    #     thread = Thread(target=camera_setup, name='camera_setup', args=([self]))
    #     thread.start()

    def camera_setup(self):
        self.video_cap = cv.VideoCapture(0)
        self.video_cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.video_cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.run_camera)

    def async_model_setup(self):
        """Выполняет подготовку нейронной сети в фоновом режиме."""
        def model_loader():
            time.sleep(5)
            print('Awaking!')

        self.thread = Thread(target=model_loader, name='predictor_loader')  # args=([padded_image, kernel_x, conv_res_x, queue])
        self.thread.start()
        # self.run_camera()

    def run_camera(self):
        ret, frame = self.video_cap.read()
        self.main_window.central_widget.webcam_img.draw(frame)
        self.camera_timer.start(33)

    def process_image(self):
        """Реализовать создание снимка, его обработку и вывод снимка, маски, графика"""
        raise NotImplementedError


app = Application(sys.argv)  # what's sys.argv?
sys.exit(app.exec_())


