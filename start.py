# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen, CREATE_NEW_CONSOLE
import time

# список запущенных процессов
p_list = []

while True:
    user = input("[S]-Запустить сервер и клиентов, [K]-убить сервер и клиентов, [Q]-Выйти >>>")

    if user == 'S':
        # запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        p_list.append(Popen('python server.py',
                            creationflags=CREATE_NEW_CONSOLE))
        print('Сервер запущен')
        # ждем на всякий пожарный
        time.sleep(2)
        # запускаем клиентов на чтение
        for _ in range(3):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            p_list.append(Popen('python client.py localhost 8888 r',
                                 creationflags=CREATE_NEW_CONSOLE))
        print('3 клиента на чтение запущены')
        # запускаем клиента на запись случайное число
        for _ in range(2):
            # Запускаем клиентский скрипт и добавляем его в список процессов
            p_list.append(Popen('python client.py localhost 8888 w',
                                creationflags=CREATE_NEW_CONSOLE))
        print('2 клиента на запись запущены')
        print(p_list, len(p_list))
    elif user == 'K':
        print(f'Открыто процессов {len(p_list)}')
        for p in p_list:
            print(f'Закрываю {p}')
            p.kill()
        p_list.clear()
    elif user == 'Q':
        if len(p_list) != 0:
            for p in p_list:
                print(f'Закрываю {p}')
                p.kill()
            p_list.clear()
        print('Выхожу')
        break
