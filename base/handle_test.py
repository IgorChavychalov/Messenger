from base.client_query import ClientQuery
from base.client_db import session

p = ClientQuery(session)

r = p.get_massage_from_history(login='Пишущий', data='2018-08-25')
print(r)

