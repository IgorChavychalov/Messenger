import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from base.server_query import BaseQuery
from base.server_db import session
import server

class ServerWindow(QMainWindow):
    # связь с дизайном
    def __init__(self, parent=None):
        super().__init__(parent)
        self.w = uic.loadUi('GUI\server.ui', self)
        self.base = BaseQuery(session)
        self.initUT()

    def load_users(self):
        users = self.base.get_users()
        for user in users:
            self.w.listWidgetUsers.addItem(user.login)

    def load_contacts(self):
        self.w.listWidgetContacts.clear()
        login = self.w.listWidgetUsers.currentItem().text()
        try:
            contacts = self.base.get_contact(login)
            for contact in contacts:
                self.w.listWidgetContacts.addItem(str(contact))
        except Exception as e:
            print(e)



    def initUT(self):
        self.load_users()
        self.w.listWidgetUsers.itemClicked.connect(self.load_contacts)
        # отображени окна
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ServerWindow()
    sys.exit(app.exec_())
