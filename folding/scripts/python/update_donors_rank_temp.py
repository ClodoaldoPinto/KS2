import psycopg2 as db
import array

def fetchsome(cursor, chunk=10000):
   while True:
      rs = cursor.fetchmany(chunk)
      if not rs: break
      for row in rs: yield row

def stringBool(bool):
   if bool: return 'True'
   return 'False'

up = dict()
connection = db.connect("host=localhost dbname=fahstats user=cpn")
cursor = connection.cursor()
cursor.execute("select distinct n_time from usuarios_indice")
d = dict.fromkeys([row[0] for row in fetchsome(cursor)], 0)
rank_time = d.copy()

#print 'rank_0'
query = """
select usuario, n_time
from donors_production_matriz
order by pontos_0 desc, pontos_7 desc, pontos_24 desc;
"""
cursor.execute(query)
rank = 0
for linha in fetchsome(cursor):
   rank += 1
   n_time = linha [1]
   rank_time [n_time] += 1
   up [linha [0]] = \
    array.array ('l',[rank, rank_time [n_time], 0, 0, 0, 0, 0 ,0, 0, 0])

#print 'rank_24'
query = """
select usuario, n_time
from donors_production_matriz
order by pontos_0 + (pontos_7 / 7) desc, pontos_0 desc;
"""
cursor.execute(query)
rank = 0
rank_time = d.copy()
for linha in fetchsome(cursor):
   rank += 1
   n_time = linha [1]
   rank_time [n_time] += 1
   up [linha [0]] [2] = rank
   up [linha [0]] [3] = rank_time [n_time]

#print 'rank_7'
query = """
select usuario, n_time
from donors_production_matriz
order by pontos_0 + pontos_7 desc, pontos_0 desc;
"""
cursor.execute(query)
rank = 0
rank_time = d.copy()
for linha in fetchsome(cursor):
   rank += 1
   n_time = linha [1]
   rank_time [n_time] += 1
   up [linha [0]] [4] = rank
   up [linha [0]] [5] = rank_time [n_time]

#print 'rank_30'
query = """
select usuario, n_time
from donors_production_matriz
order by pontos_0 + (pontos_7 * 30 / 7) desc, pontos_0 desc;
"""
cursor.execute(query)
rank = 0
rank_time = d.copy()
for linha in fetchsome(cursor):
   rank += 1
   n_time = linha [1]
   rank_time [n_time] += 1
   up [linha [0]] [6] = rank
   up [linha [0]] [7] = rank_time [n_time]

#print 'rank_month'
query = """
select usuario, n_time
from donors_production_matriz
order by pontos_month desc, pontos_0 desc;
"""
cursor.execute(query)
rank = 0
rank_time = d.copy()
del(d)
for linha in fetchsome(cursor):
   rank += 1
   n_time = linha [1]
   rank_time [n_time] += 1
   up [linha [0]] [8] = rank
   up [linha [0]] [9] = rank_time [n_time]
del(rank_time)

#print 'insert'
query = """
prepare ins(
      int, int, float4, float4,  float4, float4, boolean, float4, int, int, int, int, int, int, int, int, int, int
      ) as
   insert into donors_production_temp (
      usuario,
      n_time,
      pontos_0,
      pontos_24,
      pontos_7,
      pontos_up,
      active,
      pontos_month,
      rank_0,
      rank_0_time,
      rank_24,
      rank_24_time,
      rank_7,
      rank_7_time,
      rank_30,
      rank_30_time,
      rank_month,
      rank_month_time
   )
   values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18);
"""
cursor.execute(query)
cursor.execute("select * from donors_production_matriz")
ins = connection.cursor()
for linha in fetchsome(cursor):
   ins.execute ("""execute ins (
      %(usuario)s,
      %(n_time)s,
      %(pontos_0)s,
      %(pontos_24)s,
      %(pontos_7)s,
      %(pontos_up)s,
      %(active)s,
      %(pontos_month)s,
      %(rank_0)s,
      %(rank_0_time)s,
      %(rank_24)s,
      %(rank_24_time)s,
      %(rank_7)s,
      %(rank_7_time)s,
      %(rank_30)s,
      %(rank_30_time)s,
      %(rank_month)s,
      %(rank_month_time)s
      );""",{
      'usuario': linha [0],
      'n_time': linha [5],
      'pontos_0': linha [3],
      'pontos_24': linha [2],
      'pontos_7': linha [1],
      'pontos_up': linha [4],
      'active': stringBool(linha [6]),
      'pontos_month': linha [7],
      'rank_0': up [linha [0]][0],
      'rank_0_time': up [linha [0]][1],
      'rank_24': up [linha [0]][2],
      'rank_24_time': up [linha [0]][3],
      'rank_7': up [linha [0]][4],
      'rank_7_time': up [linha [0]][5],
      'rank_30': up [linha [0]][6],
      'rank_30_time': up [linha [0]][7],
      'rank_month': up [linha [0]][8],
      'rank_month_time': up [linha [0]][9]
      })
cursor.close()
ins.close()
connection.commit()
connection.close()
