"""Пример из справочника (а вообще он вроде бы из документации)"""

import socket
import struct

import numpy as np
from typing import Tuple

from image_processor import ImageProcessor


class JetsonServer:
    """Класс сервера, запускаемого на Nvidia Jetson Nano.
    Функции:
    1) Опрос камеры,
    2) Сегментация изображения,
    3) Вычисление соотношения площадей сегментированных областей,
    4) Отправка результатов клиенту.
    """
    _server_address: Tuple[str, int]
    _image_processor: ImageProcessor

    def __init__(self,
                 ip: str,
                 port: int,
                 ):
        self._image_processor = ImageProcessor()
        self._server_address = (ip, port)
        self._setup()

    def _setup(self):
        """Метод предназначен для:
        1) Создания сокета,
        2) Привзяки сокета к прослушиваемому порту
        """
        self._sock = socket.socket(socket.AF_INET. socket.SOCK_STREAM)
        self._sock.bind(self._server_address)
        self._sock.listen(1)
        print(f'Server started on {self._server_address[0]} port: {self._server_address[1]}')

    def run(self):
        self._wait_connection()
        self._send()
        self._close()

    def _wait_connection(self):
        """Метод ожидает подключения от клиента."""
        while True:
            print('waiting for а connection')
            self._connection, client_address = self._sock.accept()
            print(f'Got connection from {client_address}')

    def _send(self):
        mask: np.ndarray
        ratio: Tuple[float, float, float]
        byte_mask: bytes
        byte_ratio: bytes

        mask, ratio = self._image_processor.process_frame()
        # TODO найти способ объединить эти элементы для совместной отправки
        byte_mask = mask.tobytes()
        byte_ratio = struct.pack('3f', *ratio)

        self._connection.sendall(byte_mask)

    def _close(self):
        """Метод закрывает соединение"""
        self._connection.close()
