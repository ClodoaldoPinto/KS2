import psycopg
import sys


db = psycopg.connect("host=localhost dbname=fahstats")
cursor = db.cursor()


query = """
select n_time, data, pontos, wus
from times
where
data = 5352
order by n_time, data, pontos
"""
cursor.execute(query)
rs = cursor.fetchall()

i = 0
for n_time, data, pontos, wus in rs:
  if i % 2.0 == 0:
    query = """insert into times_2 (n_time, data, pontos, wus)
values (""" + str(n_time) + ',' + str(data) + ',' + str(pontos) + ',' + str(wus) + ');'
    cursor.execute(query)
  i += 1

db.commit()


cursor.close()
db.commit()
db.close()

