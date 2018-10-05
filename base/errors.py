class LoginIsUsed(Exception):
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return f'login {self.login} is used'


class LoginIsNotInTable(Exception):
    # LoginDoseNotTable
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return f'{self.login} is not in Users table'


class IdIsNotInTable(Exception):
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return f'{self.login}ID is not in History table'


class LoginHasNoContacts(Exception):
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return f'{self.login} has no contacts'


class UsersAreNotFrends(Exception):
    def __init__(self, user, frend):
        self.user = user
        self.frend = frend

    def __str__(self):
        return f'{self.user} and {self.frend} are not frends'


class ContactIsExist(Exception):
    def __init__(self, user, frend):
        self.user = user
        self.frend = frend

    def __str__(self):
        return f'<Contact {self.user} - {self.frend} is Exist'

class UsersHasNotMessages(Exception):
    def __init__(self, user, data):
        self.user = user
        self.data = data

    def __str__(self):
        return f'{self.user} has not Messages in {data}'
# АНГЛИЙСКИЙ ЗАСТРЕЛИЛСЯ
