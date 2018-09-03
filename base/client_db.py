from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
import os
from sqlalchemy.orm import sessionmaker


FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(FOLDER, 'client.db')

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    userID = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)

    def __init__(self, login):
        self.login = login

    def __repr__(self):
        return f'{self.userID}-{self.login} '


class MessageHistory(Base):
    __tablename__ = 'MessageHistory'
    MessageHistoryID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('Users.userID'))
    dataPoint = Column(String(50))
    timePoint = Column(String(50))
    chat = Column(String(50))
    recipientID = Column(Integer, ForeignKey('Users.userID'))
    text = Column(String(50))

    def __init__(self, userID, dataPoint, timePoint, chat, recipientID, text):
        self.userID = userID
        self.dataPoint = dataPoint
        self.timePoint = timePoint
        self.chat = chat
        self.recipientID = recipientID
        self.text = text

    def __repr__(self):
        return f'{self.userID} {self.dataPoint} {self.timePoint} {self.recipientID} {self.text}'


engine = create_engine(f'sqlite:///{PATH}', echo=False)
# Приминение сртуктуры БД
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
# Запуск ссесии
session = Session()
