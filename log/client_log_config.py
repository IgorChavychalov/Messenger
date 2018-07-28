import logging.handlers
import os

# собственные модули
from settings import ENCODING

# Папка где лежит этот файл
FOLDER = os.path.dirname(os.path.abspath(__file__)) + '\\files'

# Пусть до серверного лога
PATH = os.path.join(FOLDER, 'client.log')

# Создание логгера
client_logger = logging.getLogger('client')
# Форматирование
formatter = logging.\
    Formatter(u'%(levelname)s  [%(asctime)s]  %(filename)s  [%(lineno)d]  %(funcName)s:  %(message)s')

# Создаем обработчик с ротацией файлов по дням
client_handler = logging.handlers.TimedRotatingFileHandler(PATH, when='D', encoding=ENCODING)
# Задаём формат
client_handler.setFormatter(formatter)

# Связываем логгер с обработчиком
client_logger.addHandler(client_handler)
# устанавливаем уровень логгера
client_logger.setLevel(logging.INFO)
