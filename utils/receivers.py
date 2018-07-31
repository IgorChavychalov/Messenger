from .JIM import get_message


class Receiver:
    """ Класс-получатель информации из сокета """
    def __init__(self, sock, request_queue):
        self.request_queue = request_queue
        self.sock = sock
        self.is_alive = False

    def process_message(self, msg):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            try:
                # получаем данные
                data = get_message(self.sock)
                # если сообщение
                if data.get('action'):
                    self.process_message(data)
                # если респонсе, то в очередь
                else:
                    self.request_queue.put(data)
            except Exception as e:
                print(e)

    def stop(self):
        self.is_alive = False


class ConsoleReciever(Receiver):
    """Консольный обработчик входящих сообщений"""

    def process_message(self, message):
        try:
            action = message['action']
            time_point = message['time']
            t = time_point[11:]
            if action == 'msg':
                text = message['message']
                name = message['from']
                print(f'\n[{t} от {name}]: {text}')
            elif action == 'quit':
                name = message['account_name']
                print(f'\n[{t} {name} покинул чат]')
        except:
            pass
