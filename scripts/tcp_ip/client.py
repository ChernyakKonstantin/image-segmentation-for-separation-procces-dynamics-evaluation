"""Пример из справочника (а вообще он вроде бы из документации)"""

import socket

# Создать сокет TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Подключить сокет к порту, который прослушивается сервером
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
try:
    # Отправить данные
    message = b'This is the message. It will be repeated.'
    print('sending {!r}'.format(message))
    sock.sendall(message)
    # Ждать ответа
    amount_received = 0
    amount_expected = len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received {!r}'.format(data))
finally:
    print('closing socket')
    sock.close()
