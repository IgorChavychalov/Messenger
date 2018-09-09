from base.client_db import Users, MessageHistory
from base.errors import *


class ClientQuery:
    def __init__(self, session):
        """ передача сессии """
        self.session = session

    def login_in_users_table(self, login):
        """ Проверка на наличие записи в таблице Users """
        result = self.session.query(Users).filter(Users.login == login).count()
        if result > 0:
            return result

    def add_user(self, login):
        """ Добавление нового логина в БД """
        if self.login_in_users_table(login=login) is None:
            user = Users(login=login)
            self.session.add(user)
            self.session.commit()
        else:
            raise LoginIsUsed(login=login)

    def get_user(self, login):
        """ Возвращает логина из БД """
        if self.login_in_users_table(login=login):
            result = self.session.query(Users).filter(Users.login == login).one()
            return result
        else:
            raise LoginIsNotInTable(login=login)

    def get_user_from_id(self, user_ID):
        """ Возвращает логин по ID"""
        result = self.session.query(Users).filter(Users.userID == user_ID).one()
        return result.login

    def add_message_history(self, login, time_point, text, frend_login):
        user = self.get_user(login)
        if frend_login == 'всем':
            frend_user = 1
        else:
            frend_user = self.get_user(frend_login).userID
        data_point, time_point = time_point.split(' ')
        add_history = MessageHistory(userID=user.userID, timePoint=time_point, dataPoint=data_point,
                                     chat=None, recipientID=frend_user, text=text)
        self.session.add(add_history)
        self.session.commit()

    def get_massage_from_history(self, login, data):
        user = self.get_user(login)
        if user:
            result = self.session.query(MessageHistory)\
                .filter(MessageHistory.userID == user.userID)\
                .filter(MessageHistory.dataPoint == data).all()
            return result
        else:
            raise UsersHasNotMessages(user=user, data=data)
