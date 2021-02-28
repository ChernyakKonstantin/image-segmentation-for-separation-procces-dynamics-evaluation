from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout, QMenuBar
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
import sys
import cv2 as cv
import numpy as np
import time
from threading import Thread
from queue import Queue

class LabeledCanvas(QWidget):
    # Класс для отрисовки изображений
    empty_image = QImage(np.zeros([100, 100, 3], dtype='uint8'), 100, 100, QImage.Format_RGB888)  # Not fully correct

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QColor(130, 120, 190))
        self.setAutoFillBackground(True)
        self.setPalette(self.palette)

        self.label = QLabel(self)
        self.image = QLabel(self)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.label)
        layout.addWidget(self.image)

        self.label.setText(title)
        self.image.setPixmap(QPixmap.fromImage(LabeledCanvas.empty_image))
        # self.image.setScaledContents(True)

    def draw(self, image: np.ndarray):
        rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        # frame_size = self.frameSize()
        target_shape = (320, 180)
        resized_image = cv.resize(rgb_image, target_shape)
        q_image = QImage(resized_image, *target_shape, 3 * target_shape[0], QImage.Format_RGB888)  # Not fully correct
        pixmap = QPixmap.fromImage(q_image)
        self.image.setPixmap(pixmap)


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        self.setLayout(h_layout)

        self.webcam_img = LabeledCanvas('Image')
        self.segmented_img = LabeledCanvas('Segmentation')
        self.chart_img = LabeledCanvas('Chart')

        v_layout.addWidget(self.webcam_img)
        v_layout.addWidget(self.segmented_img)

        h_layout.addLayout(v_layout)
        h_layout.addWidget(self.chart_img)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Separator Dynamics Estimator')
        self.status_bar = QStatusBar()
        self.menu_bar = QMenuBar()
        self.central_widget = CentralWidget()
        self.setStatusBar(self.status_bar)
        self.setMenuBar(self.menu_bar)
        self.setCentralWidget(self.central_widget)
        self.showFullScreen()

        self.status_bar.showMessage('Hello, user!')
        self.menu_bar.addAction('Quit', self.close)


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera_setup()
        # self.predictor = None
        # self.async_model_setup()

        self.main_window = MainWindow()

        self.run_camera()

    def camera_setup(self):
        self.video_cap = cv.VideoCapture(0)
        self.video_cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.video_cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.run_camera)

    def async_model_setup(self):
        def model_loader():
            time.sleep(5)
            print('Awaking!')

        self.thread = Thread(target=model_loader, name='predictor_loader')  # args=([padded_image, kernel_x, conv_res_x, queue])
        self.thread.start()

    def run_camera(self):
        ret, frame = self.video_cap.read()
        self.main_window.central_widget.webcam_img.draw(frame)
        self.camera_timer.start(33)


app = Application(sys.argv)  # what's sys.argv?
sys.exit(app.exec_())


