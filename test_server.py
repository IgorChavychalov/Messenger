import pytest
import server


class BaseHandler:
    pass


class TestJsonHandler:

    def setup(self):
        self.user = server.JsonHandler(BaseHandler)

    def test_create_presence(self):
        presence = self.user.create_presence()
        assert presence['action'] == 'presence'
        assert presence['account_name'] == 'Name'
        assert presence['password'] == 'password'

# Не чего не понятно!

if __name__ == "__main__":
    pytest.main()
