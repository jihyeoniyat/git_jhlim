from smsdk import client
from datetime import datetime, timedelta
import pandas as pd
import time
import ndjson

start = time.time()

cli = client.Client('hansol-dj')

cli.login('apikey',
          key_id = '0ca27097-75f7-4ff7-8e34-5050a2e62225',
          secret_id = 'sma_uHgU9zTEFLXQqp5tpuHWsWIVExkyRNqhMm9v971d0OJ_')


machine_types = cli.get_machine_type_names()
machines = cli.get_machine_names(source_type=machine_types[15])
columns = cli.get_machine_schema(machines[0])['display'].to_list()
query = {'Machine': machines[0],
         'End Time__gte' : datetime(2023, 1, 2),
         'End Time__lte' : datetime(2023, 1, 9),
         '_order_by': '-End Time',
         '_only': columns}

df = cli.get_cycles(**query)

print(f'Size of returned data: {df.shape}')
print("time :", time.time() - start)


df.head()
df.to_csv("c:/Users/limjh/OneDrive/바탕 화면/git_jhlim/smHOT_7.csv", encoding='euc-kr')
cli.logout()















# ## 수정 

# machine_types = cli.get_machine_type_names()
# machines = cli.get_machine_names(source_type=machine_types[15])
# #columns = cli.get_machine_schema(machines[0])['display'].to_list()


# column_name = cli.get_machine_schema(machines[0])
# column_name['name'] = column_name['name'].str.replace('.', '__',regex=True)
# #print(column_name)

# ##


# query = {'Machine': machines[0],
#          'End Time__gte' : datetime(2023, 1, 9),
#          'End Time__lte' : datetime(2023, 1, 10),
#          '_order_by': '-End Time',
#          '_only': 'column_name'}

# df = cli.get_cycles(**query)

# ## 컬럼명 수정
# display_dict = dict(zip(column_name.name, column_name.display))
# df.rename(columns=display_dict, inplace=True)
# ##

# print(f'Size of returned data: {df.shape}')
# print("time :", time.time() - start)


# df.head()
# df.to_csv("test2.csv", encoding='utf-8')
# cli.logout()