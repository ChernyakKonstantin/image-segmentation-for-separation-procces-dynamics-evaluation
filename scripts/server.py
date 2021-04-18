"""Модуль сервера, запускаемый на ПК, выполняющем сегментацию изображений."""

import struct
from socketserver import BaseRequestHandler, TCPServer
from typing import Tuple

import numpy as np

from image_processor import ImageProcessor


class JetsonServerHandler(BaseRequestHandler):
    """Класс обработчика запросов.
    Возвращает результат сегментации: кортеж из изображения маски фракций и кортежа долей их площадей.
    """
    def __init__(self, *args, **kwargs):
        super(JetsonServerHandler, self).__init__(*args, **kwargs)
        self._image_processor = ImageProcessor()
    
    def handle(self):
        mask: np.ndarray
        ratio: Tuple[float, float, float]
        byte_mask: bytes
        byte_ratio: bytes

        mask, ratio = self._image_processor.process_frame()
        # TODO найти способ объединить эти элементы для совместной отправки
        byte_mask = mask.tobytes()
        byte_ratio = struct.pack('3f', *ratio)

        self.request.sendall(byte_ratio)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 80

    with TCPServer((HOST, PORT), JetsonServerHandler) as server:
        print(f'Server started on {HOST}, port {PORT}')
        server.serve_forever()
