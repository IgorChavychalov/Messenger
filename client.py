import socket
import logging
from threading import Thread
from queue import Queue
import sys
import time

# собственные модули
import utils.settings
from utils.JIM import get_message, send_message
from utils.receivers import ConsoleReciever
import utils.msg
from base.client_query import ClientQuery
from base.errors import LoginIsUsed
from base.client_db import session
import log.client_log_config


logger = logging.getLogger('client')


def print_title(func):
    """ Добавляет заголовок """
    def wrap(*args, **kwargs):
        print()
        print('-'*8, "Список контактов", '-'*8)
        result = func(*args, **kwargs)
        return print(result)
    return wrap


class User:
    def __init__(self, login, password, addr, port):
        self.base = ClientQuery(session)
        self.login = login
        self.password = password
        self.addr = addr
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info(f'Запуск клиента (client {self.login})')  #
        self.contacts = []
        self.request_queue = Queue()

    def connect(self):
        try:
            self.socket.connect((self.addr, self.port))
            logger.info(f'Установлено соединение с сервером {self.addr}:{self.port})')  #
        except ValueError:
            print('Порт должен быть целым числом')
            sys.exit(0)
        # проба <-
        server_msg = get_message(self.socket)
        if server_msg['action'] == 'probe':
            logger.info(f'Получен запрос (probe) от сервера (client {self.login})')  #
            # процедура проверки связи с сервером
            self.connect_control()

    def create_presence(self):
        presence = utils.msg.Presence(account_name=self.login, password=self.password).pack()
        return presence

    def create_close_msg(self):
        message = utils.msg.Quit(self.login).pack()
        return message

    def create_message(self, text, to_name):
        message = utils.msg.Message(msg=text, from_name=self.login, to_name=to_name).pack()
        return message

    def create_add_contact_msg(self, new_frend):
        message = utils.msg.AddContact(new_frend, action=1).pack()
        return message

    def create_get_contact_msg(self):
        message = utils.msg.GetContacts().pack()
        return message

    def create_del_contact_msg(self, del_frend):
        message = utils.msg.AddContact(del_frend).pack()
        return message

    def response_control(self, response_msg):
        response = response_msg['response']
        alert = response_msg['alert']
        if response == 200:
            logger.info(f'Получен ответ сервера на презентс (200) (client {self.login})  {alert}')  #
            return alert
        else:
            # ошибка
            logger.error(f'нет ответа от сервера на презентс (client {self.login})  {alert}')  #
            pass

    def connect_control(self):
        """ Процедура опроса клиента """

        # презентс ->
        presence = self.create_presence()
        send_message(socket=self.socket, message=presence)
        logger.info(f'Отправлен презент серверу (client {self.login})')  #
        # респонс <-
        response = get_message(self.socket)
        # респонс <!>
        self.response_control(response)
        return

    def update_contacts(self):
        cod, contacts = self.get_contacts()
        if cod == 200:
            self.contacts = contacts
            logger.info(f' Обнавлён список контактов (client {self.login}) {self.contacts}')  #

    @print_title
    def show_contacts(self):
        return self.contacts

    def get_contacts(self):
        """ Запрашивает список контактов и возвращает их с сод ответа"""
        msg = self.create_get_contact_msg()
        send_message(socket=self.socket, message=msg)
        logger.info(f'Отправлен запрос "список контактов" (client {self.login})  {msg}')  #
        response = self.request_queue.get()
        logger.info(f'Получен ответ от сервера {response}')  #
        contacts = response['alert']
        cod = response['response']
        return cod, contacts

    def add_contact(self, login):
        # нужна проверка на наличие логина в списке контаков пользователя
        msg = self.create_add_contact_msg(login)
        send_message(socket=self.socket, message=msg)
        logger.info(f'Отправлен запрос на добавление контакта (client {self.login} {msg})')  #
        response = self.request_queue.get()
        logger.info(f'Получен ответ от сервера {response}')  #
        return response

    def del_contact(self, login):
        # нужна проверка на наличие логина в списке контаков пользователя
        msg = self.create_del_contact_msg(login)
        send_message(socket=self.socket, message=msg)
        logger.info(f'Отправлен запрос на удаление контакта (client {self.login} {msg})')  #
        response = self.request_queue.get()
        logger.info(f'Получен ответ от сервера {response}')  #
        return response

    def quit_process(self):
        message = self.create_close_msg()
        send_message(socket=self.socket, message=message)
        logger.info(f'Отправлено уведомление о выходе на сервер (client {self.login})  {message}')  #
        response = self.request_queue.get()
        self.print_response(response)
        logger.info(f'Произведён выход (client {user.login})')  #
        self.socket.close()

    def print_response(self, msg):
        alert = msg['alert']
        time_point = msg['time']
        t = time_point[11:]
        print(f'[{t} сервер] {alert}')

    def write_massage(self, to_name):
        text = None
        while text != 'Q':
            text = input('\r[?]-опции. Сообщение всем >>>')
            if text == 'Q':
                # процедура выхода
                self.quit_process()
            elif text == '?':
                print('[Q]-выход \n[A:name]-добавить контакт (для теста Смелый)'
                      ' \n[D:name]-удалить контакт (для теста Смелый)'
                      ' \n[L]-получить список контатков')
            elif text.startswith('A:'):
                # добавление нового контакта
                command, name = text.split(':')
                answer = self.add_contact(name)
                # запрашиваем список контактов
                self.print_response(answer)
                if answer['response'] == 201:
                    self.update_contacts()
                self.show_contacts()
            elif text == 'L':
                # запрашиваем список контактов
                self.show_contacts()
            elif text.startswith('D:'):
                # удаление контакта
                command, name = text.split(':')
                answer = self.del_contact(name)
                # запрашиваем список контактов
                self.print_response(answer)
                if answer['response'] == 203:
                    self.update_contacts()
                self.show_contacts()
            else:
                if text != '':
                    # отправка простого сообщения
                    message = self.create_message(to_name=to_name, text=text)
                    self.base.add_message_history(login=message['from'], time_point=message['time'],
                                                  text=text, frend_login=message['to'])
                    logger.info(f'Отправлено сообщение на сервер (client {self.login})  {message}')  #
                    send_message(socket=self.socket, message=message)


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = utils.settings.ADDR
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = utils.settings.PORT
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)
    try:
        login = str(sys.argv[3])
    except IndexError:
        login = 'Пишущий'

    user = User(login=login, password='2', port=port, addr=addr)
    user.connect()

    listener = ConsoleReciever(user.socket, user.request_queue)
    th_listen = Thread(target=listener.poll)
    th_listen.daemon = True
    th_listen.start()
    try:
        user.base.add_user(login='all')
    except LoginIsUsed:
        logger.info(f'пользователь {all}, уже добавлен')
    try:
        user.base.add_user(login=user.login)
    except LoginIsUsed:
        logger.info(f'пользователь {all}, уже добавлен')
    user.update_contacts()
    user.write_massage('all')
