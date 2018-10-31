from subprocess import Popen, CREATE_NEW_CONSOLE
import time


Popen('python server.py localhost 8888',
                    creationflags=CREATE_NEW_CONSOLE)
print('Сервер запущен')
# ждем на всякий пожарный
time.sleep(2)
# запускаем 2 клиентов
# Popen('python client_GUI.py localhost 8888 Клиент', creationflags=CREATE_NEW_CONSOLE)
# Popen('python client_GUI.py localhost 8888 Пациент', creationflags=CREATE_NEW_CONSOLE)
Popen('python client_GUI.py localhost 8888 Клиент')
Popen('python client_GUI.py localhost 8888 Пациент')
print('запущенно 2 клиента')
