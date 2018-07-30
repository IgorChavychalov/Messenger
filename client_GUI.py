import sys
from PyQt5 import uic, Qt, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
import client
import jim.JIM
import jim.msg


class UserWindow(QMainWindow):
    def __init__(self, login, password, parent=None):
        super().__init__(parent)
        self.login = login
        self.password = password
        self.user = client.User(login=login, password=password)
        self.user.connect()

        self.w = uic.loadUi('GUI\client.ui', self)
        self.w.setWindowTitle(self.login)
        self.contacts = []
        self.initUT()

    def set_contacts(self):
        self.w.listWidgetContacts.clear()
        for contact in self.contacts:
            self.w.listWidgetContacts.addItem(str(contact))

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
            self.wc = Chat(socket=self.user.socket, login=self.login)
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


class Chat(Qt.QWidget):
    def __init__(self, socket, login):
        super().__init__()
        self.socket = socket
        self.login = login
        self.chat = uic.loadUi('GUI\chat.ui')
        self.chat.show()
        self.chat.setWindowTitle('Общий чат')

        self.initUI()

    def send_msg(self):
        try:
            text = self.chat.textEdit.toPlainText()
            msg = self.create_message(text=text, to_name=self.login)
            jim.JIM.send_message(socket=self.socket, message=msg)
            self.chat.textEdit.clear()
            self.print_msg(msg)
        except Exception as e:
            print(e)

    def print_msg(self, msg):
        alert = msg['message']
        time_point = msg['time']
        t = time_point[11:]
        text = f'[{t} {self.login}] {alert}'
        self.chat.textBrowser.append(text)

    def create_message(self, text, to_name):
        message = jim.msg.Message(msg=text, from_name=self.login, to_name=to_name).pack()
        return message

    def initUI(self):
        self.chat.pushButtonSend.clicked.connect(self.send_msg)


if __name__ == '__main__':
    login = 'Пишуший'
    password = '2'
    app = QApplication(sys.argv)
    ex = UserWindow(login=login, password=password)
    sys.exit(app.exec_())