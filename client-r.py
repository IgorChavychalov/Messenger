import socket
import logging
import time
import sys
import log.client_log_config

# собственные модули
import settings
import jim.JIM
import jim.msg

logger = logging.getLogger('client')


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        logger.info(f'Запуск клиента (client {self.login})')  #

    def create_presence(self):
        presence = jim.msg.Presence(account_name=self.login, password=self.password).pack()
        return presence

    def create_close_msg(self):
        message = jim.msg.Quit(self.login).pack()
        return message

    def create_message(self, text, to_name):
        message = jim.msg.Message(msg=text, from_name=self.login, to_name=to_name).pack()
        return message

    def response_control(self, response_msg):
        response = response_msg['response']
        alert = response_msg['alert']
        if response == 200:
            logger.info(f'Получен ответ сервера на презентс (200) (client {self.login})  {alert}')  #
            return
        else:
            # ошибка
            logger.error(f'нет ответа от сервера на презентс (client {self.login})  {alert}')  #
            pass

    def connect_control(self, socket):
        """ Процедура опроса клиента"""
        # презентс ->
        presence = self.create_presence()
        jim.JIM.send_message(socket=socket, message=presence)
        logger.info(f'Отправлен презент серверу (client {self.login})')  #
        # респонс <-
        response = jim.JIM.get_message(socket)
        # респонс <!>
        self.response_control(response)
        return

    def write_massage(self, socket, to_name):
        text = None
        while text != 'Q':
            text = input('[Q]-выход \nСообщение всем >>>')
            if text == 'Q':
                # процедура выхода
                message = self.create_close_msg()
                logger.info(f'Отправлено уведомление о выходе на сервер (client {self.login})  {message}')  #
            else:
                message = self.create_message(to_name=to_name, text=text)
                logger.info(f'Отправлено сообщение на сервер (client {self.login})  {message}')  #
            jim.JIM.send_message(socket=socket, message=message)

    def read_massage(self, socket):
        while True:
            try:
                message = jim.JIM.get_message(socket)
                action = message['action']
                time_point = message['time']
                t = time_point[11:]
                if action == 'msg':
                    text = message['message']
                    name = message['from']
                    print(f'[{t} от {name}]: {text}')
                elif action == 'quit':
                    name = message['account_name']
                    print(f'[{t} {name} покинул чат]')
            except:
                pass


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = settings.ADDR
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = settings.PORT
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)
    try:
        mode = sys.argv[3]
    except IndexError:
        mode = 'r'

    client.connect((addr, port))
    user = User(login='Читающий', password='2')

    logger.info(f'Запуск клиента (client {user.login})')  #
    logger.info(f'Установлено соединение с сервером {addr}:{port})')  #
    # проба <-
    server_msg = jim.JIM.get_message(client)

    if server_msg['action'] == 'probe':
        logger.info(f'Получен запрос (probe) от сервера (client {user.login})')  #
        # процедура проверки связи с сервером
        user.connect_control(client)

    if mode == 'w':
        user.write_massage(socket=client, to_name='всем')
    elif mode == 'r':
        user.read_massage(client)

    time.sleep(2)  # необходимо что бы сообщение Quit дошло до сервера
    logger.info(f'Произведён выход (client {user.login})')  #
