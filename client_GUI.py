import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import pyqtSlot, QThread
# собственные модули
import client
import utils.JIM
import utils.msg
import utils.settings
import datetime
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
            self.wc.refresh_msg_list()
        except Exception as e:
            print(e)

    def refresh_contacts(self):
        self.contacts = self.user.get_contacts()[1]
        self.set_contacts()

    def add_contact(self):
        contact = self.w.lineEditAddContact.text()
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

    def open_avatar(self):
        try:
            self.fname = QFileDialog.getOpenFileName(self)
            pixmap = QPixmap(self.fname[0])
            t = pixmap.scaled(180, 180, QtCore.Qt.KeepAspectRatio)
            self.w.lblAvatar.setPixmap(t)
        except Exception as e:
            print(e)

    def del_contact(self):
        contact = self.w.lineEditAddContact.text()
        answer = self.user.del_contact(contact)
        if answer['response'] == 203:
            self.refresh_contacts()
        self.print_info(answer)

    def set_item(self):
        name = self.w.listWidgetContacts.currentItem().text()
        self.w.lineEditAddContact.setText(name)

    def initUT(self):
        self.refresh_contacts()  # получаем контакты
        self.w.pushButtonAddContact.clicked.connect(self.add_contact)
        #self.w.pushButtonOpenChat.clicked.connect(self.open_chat)
        self.w.pushButtonDelContact.clicked.connect(self.del_contact)
        self.w.listWidgetContacts.itemClicked.connect(self.set_item)
        self.w.listWidgetContacts.itemDoubleClicked.connect(self.open_chat)
        self.w.pushButton.clicked.connect(self.open_avatar)
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
            rows = self.user.base.get_massage_from_history(data=data)
            self.chat.textBrowser.clear()
            if rows:
                for row in rows:
                    login_id = row.userID
                    login = self.user.base.get_user_from_id(login_id)
                    time_p = row.timePoint
                    res = row.recipientID
                    txt = row.text

                    if not login == self.login:
                        form_row = f'[{time_p} от {login}] '
                        self.chat.textBrowser.append(form_row)
                        self.chat.textBrowser.insertHtml(txt)
                    else:
                        form_row = f'[{time_p}] '
                        self.chat.textBrowser.setTextColor(QColor("green"))
                        self.chat.textBrowser.append(form_row)
                        self.chat.textBrowser.insertHtml(f"<div><font color=\"green\">{txt}</font></div>")
                        self.chat.textBrowser.setTextColor(QColor("black"))
                    self.chat.textBrowser.ensureCursorVisible()
        except Exception as e:
            print(e)

    def send_msg(self):
        try:
            text = self.chat.textEdit.toHtml()
            msg = self.create_message(text=text, to_name=self.login)
            self.user.base.add_message_history(login=self.login, time_point=msg['time'],
                                                   text=text, frend_login=msg['to'])
            utils.JIM.send_message(socket=self.socket, message=msg)
            self.refresh_msg_list()
        except Exception as e:
            print(e)

    def refresh_msg_list(self):
        self.chat.textEdit.clear()
        self.load_history_msg(data=str(datetime.date.today()))

    def create_message(self, text, to_name):
        message = utils.msg.Message(msg=text, from_name=self.login, to_name=to_name).pack()
        return message

    # def set_smile(self):
    #     """ дабовление смайликов в панель и создание связи с действием"""
    #     smile_src = r'picture_button\smile.jpg'
    #     smile_name = 'smile'
    #     self.chat.textEdit.textCursor().insertHtml('<img src="%s" />' % smile_src)

    def set_smile(self, src):
        smile_src = r'picture_button\smile.jpg'
        # создание связи кнопки с действие (лямда для передачи аргмента)
        self.chat.textEdit.textCursor().insertHtml('<img src="%s" />' % smile_src)

    def set_melancholy(self, src):
        smile_src = r'picture_button\melancholy.jpg'
        # создание связи кнопки с действие (лямда для передачи аргмента)
        self.chat.textEdit.textCursor().insertHtml('<img src="%s" />' % smile_src)

    # def set_format(self, font_src, font_name, toolbar):
    #     """ дабовление эффектов шрифта в панель и создание связи с действием """
    #     font = QAction(QIcon(font_src), font_name, self)
    #     # создание связи кнопки с действие
    #     tag = font_name[:1]  # используем название файлов до точки ([i].jpg)
    #     font.triggered.connect(lambda: self.change_font(tag))
    #     toolbar.addAction(font)
    #
    # def change_font(self, tag):
    #     """ вставить элемент в текст """
    #     selected_text = self.textEdit.textCursor().selectedText()
    #     self.textEdit.textCursor().insertHtml(
    #         '<{tag}>{val}</{tag}>'.format(val=selected_text, tag=tag))

    def initUI(self):
        # ссылки на иконки
        SMILE_SRC = r'picture_button\smile.jpg'
        MELANCHOLY_SRC = r'picture_button\melancholy.jpg'
        BOLT_SRC = r'picture_button\b.jpg'
        ITALIC_SRC = r'picture_button\i.jpg'

        self.chat.btnSmile.clicked.connect(self.set_smile)
        self.chat.btnMelancholy.clicked.connect(self.set_melancholy)
        self.load_history_msg(data=str(datetime.date.today()))
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
