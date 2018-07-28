from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
import os
from sqlalchemy.orm import sessionmaker


FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(FOLDER, 'server.db')

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    userID = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    info = Column(String, nullable=True)

    def __init__(self, login, info=None):
        self.login = login
        if info:
            self.info = info

    def __repr__(self):
        return f'<Users: {self.userID} : {self.login} : {self.info}>'


class History(Base):
    __tablename__ = 'History'
    historyID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('Users.userID'))
    timePoint = Column(String(50))
    addressIP = Column(String)
    action = Column(String)

    def __init__(self, userID, timePoint, addressIP, action):
        self.userID = userID
        self.timePoint = timePoint
        self.addressIP = addressIP
        self.action = action

    def __repr__(self):
        return f'<History: {self.userID} {self.timePoint} {self.addressIP} {self.action}>'


class Contacts(Base):
    __tablename__ = 'Contacts'
    contactID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('Users.userID'))
    frendID = Column(Integer, ForeignKey('Users.userID'))

    def __init__(self, userID, frendID):
        self.userID = userID
        self.frendID = frendID

    def __repr__(self):
        return f'{self.userID} - {self.frendID}'


engine = create_engine(f'sqlite:///{PATH}', echo=False)
# Приминение сртуктуры БД
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
# Запуск ссесии
session = Session()
