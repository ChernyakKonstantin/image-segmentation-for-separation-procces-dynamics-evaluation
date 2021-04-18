"""Пример из справочника (а вообще он вроде бы из документации)"""

import socket

# Создать сокет TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Привязать сокет к прослушиваемому порту
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
# Слушать входящие соединения
sock.listen(1)
while True:
    # Ждать соединения
    print('waiting for а connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        # Получать данные небольшими порциями и
        # отправлять их обратно
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no data from', client_address)
                break
    finally:
        # Закрыть соединение
        connection.close()
