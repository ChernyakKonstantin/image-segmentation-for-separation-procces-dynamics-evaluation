"""Модуль, содержащий класс TCP-клиента.
Впоследствии класс будет перемещен в модуль приложения.
"""
import socket


class Client:
    """Класс TCP-клиента, опрашивающего сервер для получения результатов сегментации."""
    def __init__(self, ip: str, port: int):
        self._address = (ip, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(self._address)

    def receive(self):
        raise NotImplementedError  # received = str(self._sock.recv(1024), "utf-8")
