from base.client_db import Users, MessageHistory
from base.errors import *
import logging
# если запрос ни чего не нашёл
from sqlalchemy.orm.exc import NoResultFound
logger = logging.getLogger('server')


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
        """ Вызов логина из БД """
        if self.login_in_users_table(login=login):
            result = self.session.query(Users).filter(Users.login == login).one()
            return result
        else:
            raise LoginIsNotInTable(login=login)

    def get_user_from_id(self, id):
        result = self.session.query(Users).filter(Users.userID == id).one()
        return result.login

    #
    # def get_users(self):
    #     """ Возвращает всех пользователей """
    #     return self.session.query(Users).all()
    #
    # def del_user(self, login):
    #     """ Удаление логина из БД """
    #     user = self.get_user(login=login)
    #     if user:
    #         self.session.delete(user)
    #         self.session.commit()
    #
    # def contact_in_contact_table(self, user_id, frend_id):
    #     """ Проверка на наличие пары ID в таблице Contact """
    #     find = self.session.query(Contacts).filter(
    #         Contacts.userID == user_id).filter(Contacts.frendID == frend_id).first()
    #     if find is not None:
    #         return find
    #
    # def add_contact(self, you_login, frend_login):
    #     """ Добавление нового контакта в БД """
    #     # получаем id и проверяем существования пользователей
    #     user = self.get_user(you_login)
    #     frend = self.get_user(frend_login)
    #     # если контакт ещё не создан, то
    #     if not self.contact_in_contact_table(user_id=user.userID, frend_id=frend.userID):
    #         # создаём контакт
    #         contact = Contacts(userID=user.userID, frendID=frend.userID)
    #         self.session.add(contact)
    #         self.session.commit()
    #     else:
    #         raise ContactIsExist(you_login, frend_login)
    #
    # def get_contact(self, login):
    #     """ Возвращает список контактов из БД """
    #     # получаем id и проверяем существования пользователей
    #     result = []
    #     user = self.get_user(login)
    #     contacts = self.session.query(Contacts).filter(Contacts.userID == user.userID).all()
    #     # формирование списка по ID
    #     if contacts:
    #         for one_contact in contacts:
    #             contact = self.session.query(Users).filter(Users.userID == one_contact.frendID).first()
    #             result.append(contact.login)
    #         return result
    #     else:
    #         raise LoginHasNoContacts(user)
    #
    # def del_contact(self, you_login, del_login):
    #     """ Удаление контакта по логину """
    #     # получаем id и проверяем существования пользователей
    #     user = self.get_user(you_login)
    #     del_user = self.get_user(del_login)
    #     # проверяем существование контакта
    #     if self.contact_in_contact_table(user_id=user.userID, frend_id=del_user.userID):
    #         contact = self.session.query(Contacts)\
    #             .filter(Contacts.userID == user.userID)\
    #             .filter(Contacts.frendID == del_user.userID).first()
    #         self.session.delete(contact)
    #         self.session.commit()
    #     else:
    #         raise UsersAreNotFrends(you_login, del_login)
    #
    # def user_id_in_visit_history_table(self, user_id):
    #     """ Проверка на наличие ID логина в таблице History """
    #     result = self.session.query(VisitHistory).filter(VisitHistory.userID == user_id).count()
    #     return result
    #
    # def get_visit_history(self, login):
    #     """ НЕОБХОДИМО РЕАЛИЗОВАТЬ ВЫЗОВ ЧЕРЕЗ КРИТЕРИЙ: ДАТА """
    #     # получаем id и проверяем наличие пользователя
    #     user = self.get_user(login)
    #     # проверяем наличие записи для данного ID в History
    #     if self.user_id_in_visit_history_table(user.userID):
    #         result = self.session.query(VisitHistory).filter(VisitHistory.userID == user.userID).first()
    #         return result
    #     else:
    #         raise IdIsNotInTable(login=login)
    #
    # def add_visit_history(self, login, time_point, address_IP, action):
    #     """ Добавление новый записии в таблице History пользователя """
    #     user = self.get_user(login)
    #     add_history = VisitHistory(userID=user.userID, timePoint=time_point,
    #                       addressIP=address_IP, action=action)
    #     self.session.add(add_history)
    #     self.session.commit()

    def add_message_history(self, login, time_point, text, frend_login):
        user = self.get_user(login)
        if frend_login == 'всем':
            frend_user = 1
        else:
            frend_user = self.get_user(frend_login).userID
        data_time = time_point.split(' ')
        add_history = MessageHistory(userID=user.userID, timePoint=data_time[1], dataPoint=data_time[0],
                                     chat=None, recipientID=frend_user, text=text)
        self.session.add(add_history)
        self.session.commit()

    def get_massage_from_history(self, data):
        # user = self.get_user(login)
        # if user:
            # result = self.session.query(MessageHistory)\
            #     .filter(MessageHistory.userID == user.userID).filter(MessageHistory.dataPoint == data).all()
        result = self.session.query(MessageHistory) \
            .filter(MessageHistory.dataPoint == data).all()

        return result
