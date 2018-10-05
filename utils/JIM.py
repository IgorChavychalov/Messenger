# сторонние модули
import json
# собственные модули
from .settings import ENCODING


def dict_to_bytes(message_dict):
    """
    Преобразование словаря в байты
    :param message_dict: словарь
    :return: bytes
    """
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict)
        # Переводим json в байты
        bmessage = jmessage.encode(ENCODING)
        # Возвращаем байты
        return bmessage
    else:
        raise TypeError


def bytes_to_dict(message_bytes):
    """
    Получение словаря из байтов
    :param message_bytes: сообщение в виде байтов
    :return: словарь сообщения
    """
    # Если переданы байты
    if isinstance(message_bytes, bytes):
        # Декодируем
        jmessage = message_bytes.decode(ENCODING)
        # Из json делаем словарь
        message = json.loads(jmessage)
        # Если там был словарь
        if isinstance(message, dict):
            # Возвращаем сообщение
            return message
        else:
            # Нам прислали неверный тип
            raise TypeError
    else:
        # Передан неверный тип
        raise TypeError


def send_message(socket, message):
    """
    Отправка сообщения
    :param socket: сокет
    :param message: словарь сообщения
    :return: None
    """
    # Словарь переводим в байты
    bprescence = dict_to_bytes(message)
    # Отправляем
    socket.send(bprescence)


def get_message(socket):
    """
    Получение сообщения
    :param socket:
    :return: словарь ответа
    """
    # Получаем байты
    bresponse = socket.recv(1024)
    # переводим байты в словарь
    response = bytes_to_dict(bresponse)
    # возвращаем словарь
    return response
