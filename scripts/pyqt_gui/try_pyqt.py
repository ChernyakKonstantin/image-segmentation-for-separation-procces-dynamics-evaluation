from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStatusBar, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
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
        self.label = QLabel(self)
        self.image = QLabel(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.image)

        self.setLayout(layout)

        self.label.setText(title)
        self.image.setPixmap(QPixmap.fromImage(LabeledCanvas.empty_image))


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        v_layout.addWidget(QLabel('Idi'))
        v_layout.addWidget(QLabel('Nahui'))

        self.setLayout(h_layout)

        self.webcam_img = LabeledCanvas('PES')
        h_layout.addWidget(self.webcam_img)
        h_layout.addLayout(v_layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Separator Dynamics Estimator')
        self.central_widget = CentralWidget()
        self.setCentralWidget(self.central_widget)
        self.show()


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera_setup()
        self.predictor = None

        self.main_window = MainWindow()

        self.run_camera()

    def camera_setup(self):
        self.video_cap = cv.VideoCapture(0)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.run_camera)

    def model_setup(self):
        time.sleep(15)

    def run_camera(self):
        ret, frame = self.video_cap.read()
        image = QImage(cv.cvtColor(frame, cv.COLOR_BGR2RGB).data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)  # Not fully correct
        pixmap = QPixmap.fromImage(image)
        self.main_window.central_widget.webcam_img.image.setPixmap(pixmap)
        self.camera_timer.start(33)



app = Application(sys.argv)  # what's sys.argv?
sys.exit(app.exec_())


