import logging.handlers
import os

# собственные модули
from utils.settings import ENCODING

# Папка где лежит этот файл
FOLDER = os.path.dirname(os.path.abspath(__file__)) + '\\files'

# Пусть до серверного лога
PATH = os.path.join(FOLDER, 'server.log')

# Создание логгера
server_logger = logging.getLogger('server')
# Форматирование
formatter = logging.\
    Formatter(u'%(levelname)s  [%(asctime)s]  %(filename)s  [%(lineno)d]  %(funcName)s:  %(message)s')

# Создаем обработчик с ротацией файлов по дням
server_handler = logging.handlers.TimedRotatingFileHandler(PATH, when='D', encoding=ENCODING)
# Задаём формат
server_handler.setFormatter(formatter)

# Связываем логгер с обработчиком
server_logger.addHandler(server_handler)
# устанавливаем уровень логгера
server_logger.setLevel(logging.DEBUG)


