import psycopg2 as db
import sys
connection = db.connect("host=localhost dbname=fahstats user=cpn")
cursor = connection.cursor()
insert = connection.cursor()

def fetchsome(cursor, chunk=50000):
   while True:
      rs = cursor.fetchmany(chunk)
      if not rs: break
      for row in rs: yield row

query = """
select
   extract(day from current_timestamp)::integer,
   extract(hour from current_timestamp)::integer;
"""    
cursor.execute(query)
day, hour = cursor.fetchall()[0]

if not(day != 1 or hour < 1 or hour > 3):
   connection.close()
   sys.exit()

query = """
prepare insert_query(integer, real, integer, integer) as
insert into donor_monthly
(donor, points, team_rank, batch)
values ($1, $2, $3, $4);
"""
cursor.execute(query);

query = """
select um.data from (
   select distinct u.data
   from usuarios as u
   inner join datas as d on d.data_serial = u.data
   where
      date_trunc('day', d.data) = date_trunc('day',
         (
         d.data + interval '1 month')::date -
         extract('day' from d.data + interval '1 month')::integer
         )
      and
      extract('month' from d.data) < extract('month' from current_date at time zone 'utc')
      and
      d.data_serial = (select data_serial
         from datas
         where date_trunc('day', d.data) = date_trunc('day', data)
         order by data desc
         limit 1)
   union
   select distinct data
   from donors_old) as um
inner join datas as d on d.data_serial = um.data
order by d.data desc;
"""
cursor.execute(query)
rs = [row[0] for row in cursor.fetchall()]
print rs

query = """
select distinct batch
from donor_monthly
"""
cursor.execute(query)
dm = dict.fromkeys([row[0] for row in cursor.fetchall()])
print dm

query = """
select d0.donor,
   d0.points - coalesce(d1.points, 0) as points, n_time
from union_monthly_rank(%s) as d0
left outer join union_monthly_rank(%s) as d1
   on d0.donor = d1.donor
inner join usuarios_indice as ui
   on ui.usuario_serial = d0.donor
order by n_time, points desc
;
"""

for i, batch in enumerate(rs[:-1]):
   #if i > 1: break
   if batch in dm: continue      
   print i, batch, rs[i +1]

   cursor.execute(query, (batch, rs[i +1]))
   rsi = fetchsome(cursor)

   team0 = -1
   for (donor, points, team) in rsi:
      if team == team0: rank += 1
      else: rank = 1
      insert.execute("execute insert_query(%s, %s, %s, %s)", (donor, points, rank, batch))
      team0 = team
      
   connection.commit()

connection.close()
