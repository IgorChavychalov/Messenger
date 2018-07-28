import pytest
import client


class TestUser:

    def setup(self):
        self.user = client.User('Name', 'password')

    def test_create_presence(self):
        presence = self.user.create_presence()
        assert presence['action'] == 'presence'
        assert presence['user']['account_name'] == 'Name'
        assert presence['user']['password'] == 'password'

    def test_create_close_msg(self):
        close_msg = self.user.create_close_msg()
        assert close_msg['action'] == 'quit'

    def test_create_message(self):
        create_massage = self.user.create_message(text='text',
                                                  to_name='to_name')
        assert create_massage['to'] == 'to_name'
        assert create_massage['from'] == 'Name'
        assert create_massage['message'] == 'text'

    def test_response_control(self):
        response_200 = self.user.response_control(response_msg={
            'response': 200, 'alert': 'alert'})
        # метод ничего не возвращает
        assert response_200 is None
        response_400 = self.user.response_control(response_msg={
            'response': 400, 'alert': 'alert'})
        # метод должен вернуть ошибку
        assert response_400 is None


if __name__ == "__main__":
    pytest.main()
