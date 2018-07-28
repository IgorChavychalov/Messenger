from pytest import raises
import sqlalchemy.orm
from .server_db import Base, Users, History, Contacts
from .server_query import BaseQuery
from .errors import *


class TestBaseQuery:
    def setup(self):
        # Создаём суслика
        engine = sqlalchemy.create_engine(f'sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)  # импорт структуры БД
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        session = Session()
        # Создаём параметры
        self.session = session
        self.base_query = BaseQuery(session)
        # Запись в таблие User для тестов
        client = Users('Первый', 'Инфа')
        client2 = Users('Второй', 'Инфа')
        client3 = Users('Третий', 'Инфа')
        self.session.add_all([client, client2, client3])
        # Запись в таблице History для тестов
        history = History(userID=1,
                          timePoint='10:10:10',
                          addressIP='10.0.0.1:8888',
                          action='presence')
        self.session.add(history)
        # Запись в таблице Contacts для тестов
        self.session.add(Contacts(userID=1, frendID=2))

    def test_login_in_users_table(self):
        """ проверка уникальности логина а таблице Users """
        result = self.base_query.login_in_users_table
        # Логин уникальный
        assert result(login='Четвёртый') == 0
        # Логин уже имеется в базе
        assert result(login='Первый')

    def test_get_user(self):
        """ проверка запроса данных пользователя из таблицы Users """
        result = self.base_query.get_user
        # ввывод логина
        assert result(login='Первый').login == 'Первый'
        # ввывод информации
        assert result(login='Первый').info == 'Инфа'
        # пользователя нет в таблице
        with raises(LoginIsNotInTable):
            result(login='1Первый')

    def test_add_user(self):
        """ проверка добавления нового логина в таблицу Users """
        new_user = self.base_query.add_user
        # создаём нового пользователя
        new_user(login='Четвёртый', info='Инфо')
        # выводим логин
        result = self.base_query.get_user
        assert result(login='Четвёртый').login == 'Четвёртый'
        # пытаемся создать нового пользователя с занятым логином
        with raises(LoginIsUsed):
            new_user(login='Первый', info='Инфо')

    def test_user_id_in_history_table(self):
        result = self.base_query.user_id_in_history_table
        # ID = 1 соответсвует пользователяю "Первый" в наличие
        assert result(user_id=1) == 1
        # В базе нет ID = 2
        assert result(user_id=2) == 0

    def test_get_history(self):
        result = self.base_query.get_history
        # существующая запись
        assert result(login='Первый').historyID == 1
        # проверяем время
        assert result(login='Первый').timePoint == '10:10:10'
        # проверяем ip
        assert result(login='Первый').addressIP == '10.0.0.1:8888'
        # проверяем action
        assert result(login='Первый').action == 'presence'
        # Для этого пользователя нет записи в таблице истории
        with raises(IdIsNotInTable):
            result(login='Второй')

    def test_contact_in_table(self):
        result = self.base_query.contact_in_table
        # существующая запись
        assert result(user_id=1, frend_id=2) == 1
        # не существующая запись
        assert result(user_id=2, frend_id=1) is None

    def test_add_contact(self):
        result = self.base_query.add_contact
        # добавляем новый контакт
        result(you_login='Первый', frend_login='Третий')
        # вызываем новый контакт
        contact_list = self.base_query.get_contact
        assert contact_list(login='Первый')[1] == 'Третий'
        # создаём контакт с не существующим пользователем
        with raises(LoginIsNotInTable):
            result(you_login='Первый', frend_login='Четвёртый')

    def test_get_contact(self):
        result = self.base_query.get_contact
        # существующая запись
        lenght = len(result(login='Первый'))
        assert result(login='Первый')[0] == 'Второй'
        assert lenght == 1
        # у этого пользователя нет контактов
        with raises(LoginHasNoContacts):
            result(login='Второй')

    def test_del_contact(self):
        # создаём контакт +1
        self.base_query.add_contact(you_login='Первый', frend_login='Третий')
        # удаляем контакт -1
        result = self.base_query.del_contact
        result(you_login='Первый', del_login='Третий')
        with raises(UsersAreNotFrends):
            result(you_login='Второй', del_login='Третий')
        # тестим
        self.test_get_contact()

    def teardown(self):
        self.session.rollback()
