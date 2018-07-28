import pytest
import jim.msg


class TestPresence:
    def setup(self):
        self.presence = jim.msg.Presence('Name', 'Password')

    def test_init(self):
        assert self.presence.account_name == 'Name'
        assert self.presence.password == 'Password'

    def test_pack(self):
        pack = self.presence.pack()
        assert pack['account_name'] == 'Name'
        assert pack['password'] == 'Password'
        assert pack['action'] == 'presence'
        assert pack['type'] == 'status'

    # def test_type_after_pack(self):
    #     # проверка типа данных ВЫЗЫВАЕТ ОШИБКУ
    #     pack = self.presence.pack()
    #     assert type(pack) == "<class 'dict'>"


class TestProb:
    def setup(self):
        self.probe = jim.msg.Probe()

    def test_pack(self):
        pack = self.probe.pack()
        assert pack['action'] == 'probe'


class TestQuit:
    def setup(self):
        self.quit = jim.msg.Quit('на')

    def test_pack(self):
        pack = self.quit.pack()
        assert pack['action'] == 'quit'


class TestResponse:
    def setup(self):
        self.response_ok = jim.msg.Response(cod=200, alert='OK')
        self.response_no = jim.msg.Response(cod=400, alert='NOT OK')

    def test_pack_ok(self):
        pack = self.response_ok.pack()
        assert pack['response'] == 200
        assert pack['alert'] == 'OK'

    def test_pack_no(self):
        pack = self.response_no.pack()
        assert pack['response'] == 400
        assert pack['alert'] == 'NOT OK'


class TestMessage:
    def setup(self):
        self.message = jim.msg.Message(msg='Привет', from_name='Я', to_name='Этому')

    def test_init(self):
        assert self.message.msg == 'Привет'
        assert self.message.from_name == 'Я'
        assert self.message.to_name == 'Этому'

    def test_pack(self):
        pack = self.message.pack()
        assert pack['action'] == 'msg'
        assert pack['from'] == 'Я'
        assert pack['to'] == 'Этому'
        assert pack['message'] == 'Привет'


class TestChat:
    def setup(self):
        self.chat_join = jim.msg.Chat(room_name='1', action=1)
        self.chat_leave = jim.msg.Chat(room_name='1')

    def test_init(self):
        assert self.chat_join.room_name == '1'
        assert self.chat_join.action == 'join'
        assert self.chat_leave.room_name == '1'
        assert self.chat_leave.action == 'leave'

    def test_pack_join(self):
        pack = self.chat_join.pack()
        assert pack['room'] == '#1'
        assert pack['action'] == 'join'

    def test_pack_leave(self):
        pack = self.chat_leave.pack()
        assert pack['room'] == '#1'
        assert pack['action'] == 'leave'


class TestAddContact:
    def setup(self):
        self.add_contact = jim.msg.AddContact('Второй')

    def test_init(self):
        assert self.add_contact.new_frend == 'Второй'

    def test_pack(self):
        pack = self.add_contact.pack()
        assert pack['action'] == 'add_contact'
        assert pack['user_id'] == 'Второй'


if __name__ == "__main__":
    pytest.main()

