import socket
import select
import logging
import sys
import log.server_log_config

# собственные модули
import utils.settings
import utils.msg
from utils.JIM import send_message, get_message
from base.server_query import BaseQuery
from base.server_db import session
from base.errors import LoginIsUsed, LoginIsNotInTable, LoginHasNoContacts, \
    ContactIsExist, UsersAreNotFrends

logger = logging.getLogger('server')


class BaseHandler:
    def __init__(self):
        self.base_query = BaseQuery(session)

    def save_name_from_presentce(self, login):
        """
        Добавление контакта из сообщения presence в таблицу Users
        Временная мера для тестирования базы. В дальнейшем должна быть регистрация.
        """
        try:
            self.base_query.add_user(login=login)
            return logger.info(f'добавлен новый пользователь {login}')  #
        except LoginIsUsed:
            return logger.error(f'пользователь {login} уже добавлен')

    def save_history(self, msg, ip):
        """ Запись в таблицу history """
        try:
            login = msg['account_name']
            self.base_query.add_history(login=login, time_point=msg['time'],
                                        action=msg['action'], address_IP=ip)
            return logger.info(f'добавлена новый запись в таблицу History: {login}')  #
        except LoginIsNotInTable:
            return logger.error(f'не удалось добавить запись в таблицу History: {login}')

    def save_new_contact(self, you, frend):
        """ Запись в таблицу contacts """
        try:
            self.base_query.add_contact(you_login=you, frend_login=frend)
            logger.info(f'добавлена новый запись в таблицу Contacts: {you}')  #
            return 201
        except LoginIsNotInTable as e:
            logger.error(f'не удалось добавить запись в таблицу Contacts: {you}, {e}')
            return 401
        except ContactIsExist as e:
            logger.error(f'не удалось добавить запись в таблицу Contacts: {you}, {e}')
            return 402

    def save_del_contact(self, you, frend):
        """ Запись в таблицу contacts """
        try:
            self.base_query.del_contact(you_login=you, del_login=frend)
            logger.info(f'контакт удалён из таблицы Contacts: {you}')  #
            return 203
        except LoginIsNotInTable as e:
            logger.error(f'не удалось удалить контакт из таблицы Contacts: {you}, {e}')
            return 401
        except UsersAreNotFrends as e:
            logger.error(f'не удалось удалить контакт из таблицы Contacts: {you}, {e}')
            return 403

    def get_contacts_list(self, login):
        """ Запрос на список контактов """
        try:
            result = self.base_query.get_contact(login)
            logger.info(f'получен список контактов для: {login}')
            return result
        except LoginHasNoContacts:
            logger.error(f'у {login} нет контактов')


class JsonHandler:
    def __init__(self, base_handler):
        self.base_handler = base_handler
        # ==============временная мера==============
        self.sock_ip = {}
        self.sock_login = {}
        # ====Надо реализовать сохранение в БД======

    def create_new_contact(self, msg, name):
        """ Добавление нового контакта возвращает кот который не исп"""
        frend = msg['user_id']
        cod = self.base_handler.save_new_contact(you=name, frend=frend)
        return cod

    def create_del_contact(self, msg, name):
        """ Добавление нового контакта возвращает кот который не исп"""
        frend = msg['user_id']
        cod = self.base_handler.save_del_contact(you=name, frend=frend)
        return cod

    def create_contacts_list(self, name):
        result = self.base_handler.get_contacts_list(name)
        return result

    def control_presence(self, presence, ip):
        # Проверка презентс сообщения
        name = presence['account_name']
        # связываем логин с сокетом
        self.sock_login[ip] = name
        action = presence['action']
        if action == 'presence':
            # временная мера пока нет аутентификации
            self.base_handler.save_name_from_presentce(name)
            self.base_handler.save_history(msg=presence, ip=ip)
            return 200
        else:
            return 400

    def create_response(self, cod, alert=0):
        if not alert:
            alert = utils.settings.alert[cod]
        message = utils.msg.Response(cod=cod, alert=alert).pack()
        return message

    def connect_protocol(self, socket, ip):
        """ Протокол опроса клиента
        Очень много всего надо как-то переделать """
        # Связываем ip адрес и сокет
        self.sock_ip[socket] = ip
        # проба ->
        probe = utils.msg.Probe()
        probe = probe.pack()
        send_message(socket, probe)
        logger.info(f'отправленна проба на {ip} {probe}')  #
        # пресентс <-
        presence = get_message(socket)
        logger.info(f'получен презентс-сообщение от {ip}  {presence}')  #
        # пресентс <!>
        cod = self.control_presence(presence=presence, ip=ip)
        # респонс ->
        response = self.create_response(cod)
        send_message(socket, response)
        logger.info(f'отправлен ответ на презентс {ip}  {response}')  #

    def read_requests(self, r_clients, all_clients):
        messages = []
        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                logger.info(f'полученно входящее сообщение {message}')  #
                messages.append((message, sock))

            except:
                logger.info(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')  #
                print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
                all_clients.remove(sock)
        # возвращаем список кортежев
        return messages

    def write_responses(self, messages, w_clients, all_clients):
        for sock in w_clients:
            # Будем отправлять каждое сообщение всем
            for message, sock_send in messages:
                try:
                    ip = self.sock_ip[sock]
                    name = self.sock_login[ip]
                    action = message['action']
                    if action == 'msg':
                        if sock != sock_send:  # broadcast send ===========>
                            send_message(sock, message)
                            logger.info(f'сообщение отправленно {message} на сокет {sock}')  #
                    elif action == 'quit':
                        logger.info(f'полученно уведомление о выходе от {name} от сокета {sock}')  #
                        if sock != sock_send:  # broadcast send ===========>
                            send_message(sock, message)
                            logger.info(f'отправленно уведомление о выходе {name} на сокет {sock}')  #
                        else:  # отправка ответа на запрос
                            # добавить запись в таблицу History
                            self.base_handler.save_history(msg=message, ip=ip)
                            response = self.create_response(cod=202)
                            # unicast send ----------->
                            send_message(sock_send,  response)
                            logger.info(f'отправлен ответ на запрос {message} на сокет {sock}') #
                    elif action == 'get_contacts' and sock == sock_send:
                        logger.info(f'получен запрос на список контактов от сокета {sock}')  #
                        contacts = self.base_handler.get_contacts_list(name)
                        response = self.create_response(cod=200, alert=contacts)
                        # unicast send ------------>
                        send_message(sock_send, response)
                        logger.info(f'отправлен ответ на запрос {message} на сокет {sock}')  #
                    elif action == 'add_contact' and sock == sock_send:
                        logger.info(f'получен запрос на добавление контакта от сокета {sock}')  #
                        print(name, message)
                        cod = self.create_new_contact(msg=message, name=name)
                        response = self.create_response(cod=cod)
                        # unicast send ------------>
                        send_message(sock_send, response)
                        logger.info(f'отправлен ответ на запрос {message} на сокет {sock}')  #
                    elif action == 'del_contact' and sock == sock_send:
                        logger.info(f'получен запрос на добавление контакта от сокета {sock}')  #
                        print(name, message)
                        cod = self.create_del_contact(msg=message, name=name)
                        response = self.create_response(cod=cod)
                        # unicast send ------------>
                        send_message(sock_send, response)
                        logger.info(f'отправлен ответ на запрос {message} на сокет {sock}')  #

                except:  # Сокет недоступен, клиент отключился
                    print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
                    sock.close()
                    all_clients.remove(sock)


class Server:
    def __init__(self, json_handler):
        self.json_handler = json_handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.r = 0

    def bind(self, addr, port):
        self.sock.bind((addr, port))
        logger.debug('__________________З А П У С К ___ С Е Р В Е Р А ___________________________')  #
        logger.info(f'Запуск сервера с адрессом {addr}:{port}')  #

    def listen(self):
        self.sock.listen(10)
        self.sock.settimeout(0.2)

        while True:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                ip = f'{addr[0]}:{addr[1]}'
                logger.info(f'подключение с {ip}')
                # 1. Опрос клиента
                self.json_handler.connect_protocol(socket=conn, ip=ip)

            except OSError as e:
                pass  # time out вышел
            else:
                print(f"Получен запрос на соединение от {str(conn)}")
                # Добавляем клиента в список
                self.clients.append(conn)

            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                # 2. Получаем входные сообщения
                requests = self.json_handler.read_requests(r, self.clients)
                # Выполним отправку входящих сообщений
                self.json_handler.write_responses(messages=requests, w_clients=w, all_clients=self.clients)


if __name__ == '__main__':
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

    base_handler = BaseHandler()
    json_handler = JsonHandler(base_handler)

    server = Server(json_handler)
    server.bind(addr, port)
    server.listen()
