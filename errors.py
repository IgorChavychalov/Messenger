class PesenceNo(Exception):
    def __init__(self, ip):
        self.ip = ip

    def __str__(self):
        return f'!!!!!'
# Для кого это? Сервера или клиента?
# Что передовать в тексте ошибки?
