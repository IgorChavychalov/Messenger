import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import pyqtSlot, QThread
# собственные модули
import client
import utils.JIM
import utils.msg
import utils.settings
from utils.receivers import GuiReciever


class UserWindow(QMainWindow):

    def __init__(self, login, password, addr, port, parent=None):
        super().__init__(parent)
        self.login = login
        self.password = password
        self.user = client.User(login=login, password=password, addr=addr, port=port)
        self.user.connect()

        self.w = uic.loadUi('GUI\client.ui', self)
        self.w.setWindowTitle(self.login)
        # создаём рессивер для перехвата
        self.listener = GuiReciever(self.user.socket, self.user.request_queue)
        # создаём поток
        self.listener.gotData.connect(self.update_chat)
        self.th = QThread()
        # ????
        self.listener.moveToThread(self.th)
        # связываем поток с рессивером при приеме данных
        self.th.started.connect(self.listener.poll)
        # запускаем поток
        self.th.start()
        self.initUT()

    def set_contacts(self):
        self.w.listWidgetContacts.clear()
        for contact in self.contacts:
            self.w.listWidgetContacts.addItem(str(contact))

    @pyqtSlot(str)
    def update_chat(self, data):
        ''' Отображение сообщения в истории
        '''
        try:
            msg = data
            self.w.listWidgetMsg.addItem(msg)
        except Exception as e:
            print(e)

    def refresh_contacts(self):
        self.contacts = self.user.get_contacts()[1]
        self.set_contacts()

    def add_contact(self):
        contact = self.w.textEditAddContact.toPlainText()
        answer = self.user.add_contact(contact)
        if answer['response'] == 201:
            self.refresh_contacts()
        self.print_info(answer)

    def print_info(self, msg):
        alert = msg['alert']
        time_point = msg['time']
        t = time_point[11:]
        text = f'[{t} сервер] {alert}'
        self.w.info.setText(text)

    def open_chat(self):
        try:
            self.wc = Chat(socket=self.user.socket, login=self.login, user=self.user)
        except Exception as e:
            print(e)

    def del_contact(self):
        contact = self.w.textEditAddContact.toPlainText()
        answer = self.user.del_contact(contact)
        if answer['response'] == 203:
            self.refresh_contacts()
        self.print_info(answer)

    def set_item(self):
        name = self.w.listWidgetContacts.currentItem().text()
        self.w.textEditAddContact.setText(name)

    def initUT(self):
        self.refresh_contacts()  # получаем контакты
        self.w.pushButtonAddContact.clicked.connect(self.add_contact)
        self.w.pushButtonOpenChat.clicked.connect(self.open_chat)
        self.w.pushButtonDelContact.clicked.connect(self.del_contact)
        self.w.listWidgetContacts.itemClicked.connect(self.set_item)
        self.show()


class Chat(QWidget):
    def __init__(self, socket, login, user):
        super().__init__()
        self.socket = socket
        self.login = login
        self.user = user
        self.chat = uic.loadUi('GUI\chat.ui')
        self.chat.show()
        self.chat.setWindowTitle('Общий чат')

        self.initUI()

    def load_history_msg(self, data):
        try:
            rows = self.user.base.get_massage_from_history(login=self.login, data=data)
            for row in rows:
                r = str(row)
                id, dp, ch, tp, rs, txt = r.split(' ')
                login = self.user.base.get_user_from_id(id)
                form_row = f'[{tp} {login}] {txt}'
                self.chat.textBrowser.append(form_row)
        except Exception as e:
            print(e)

    def send_msg(self):
        try:
            text = self.chat.textEdit.toPlainText()
            msg = self.create_message(text=text, to_name=self.login)
            self.user.base.add_message_history(login=self.login, time_point=msg['time'],
                                                   text=text, frend_login=msg['to'])
            utils.JIM.send_message(socket=self.socket, message=msg)
            self.chat.textEdit.clear()
            self.print_msg(msg)
        except Exception as e:
            print(e)

    def print_msg(self, msg):
        try:
            alert = msg['message']
            time_point = msg['time']
            t = time_point[11:]
            text = f'[{t} {self.login}] {alert}'
            self.chat.textBrowser.append(text)
        except Exception as e:
            print(e)

    def create_message(self, text, to_name):
        message = utils.msg.Message(msg=text, from_name=self.login, to_name=to_name).pack()
        return message

    def initUI(self):
        self.load_history_msg(data='2018-08-27')
        self.chat.pushButtonSend.clicked.connect(self.send_msg)


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

app = QApplication(sys.argv)
ex = UserWindow(login=login, password='2', addr=addr, port=port)


sys.exit(app.exec_())
