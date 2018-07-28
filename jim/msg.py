import time


class Ttime:
    def __init__(self, time_point=None):
        self.time_point = time.strftime('%Y-%m-%d %H:%M:%S')


class Presence(Ttime):
    def __init__(self, account_name, password, time_point=None):
        self.password = password
        self.account_name = account_name
        super().__init__(time_point)

    def pack(self):
        result = {'action': 'presence',
                  'time': self.time_point,
                  'type': 'status',
                  'account_name': self.account_name,
                  'password': self.password}
        return result


class Probe(Ttime):
    def __init__(self, time_point=None):
        super().__init__(time_point)

    def pack(self):
        result = {'action': 'probe',
                  'time': self.time_point}
        return result


class Response(Ttime):
    def __init__(self, cod, alert=None, time_point=None):
        self.cod = cod
        self.alert = alert
        super().__init__(time_point)

    def pack(self):
        result = {'response': self.cod,
                  'time': self.time_point,
                  'alert': self.alert}
        return result


class Message(Ttime):
    def __init__(self, from_name, to_name, msg, time_point=None):
        self.from_name = from_name
        self.to_name = to_name
        self.msg = msg
        super().__init__(time_point)

    def pack(self):
        result = {'action': 'msg',
                  'time': self.time_point,
                  'to': self.to_name,
                  'from': self.from_name,
                  'message': self.msg}
        return result


class Quit(Ttime):
    def __init__(self, account_name, time_point=None):
        self.account_name = account_name
        super().__init__(time_point)

    def pack(self):
        result = {'action': 'quit',
                  'account_name': self.account_name,
                  'time': self.time_point}
        return result


class Chat(Ttime):
    """ Уведомление о покидания или присоединения к чату """
    def __init__(self, room_name, action=0, time_point=None):
        self.room_name = room_name
        if action:
            self.action = "join"
        else:
            self.action = "leave"
        super().__init__(time_point)

    def pack(self):
        room_name = '#' + self.room_name
        result = {'action': self.action,
                  'time': self.time_point,
                  'room': room_name}
        return result


class AddContact(Ttime):
    def __init__(self, frend, action=0, time_point=None):
        self.frend = frend
        if action:
            self.action = "add_contact"
        else:
            self.action = "del_contact"
        super().__init__(time_point)

    def pack(self):
        result = {'action': self.action,
                  'user_id': self.frend,
                  'time': self.time_point}
        return result


class GetContacts(Ttime):
    def __init__(self, time_point=None):
        super().__init__(time_point)

    def pack(self):
        result = {'action': 'get_contacts',
                  'time': self.time_point}
        return result


class NewClass(Ttime):
    """ Похоже я начал понимать зачем нужны метоклассы.
     А может и нет. Надо почитать """
    def __init__(self, time_point=None):
        super().__init__(time_point)
