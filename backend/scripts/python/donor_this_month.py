import psycopg2 as db
connection = db.connect("host=localhost dbname=fahstats user=cpn")
cursor = connection.cursor()
insert = connection.cursor()

def fetchsome(cursor, chunk=50000):
   while True:
      rs = cursor.fetchmany(chunk)
      if not rs: break
      for row in rs: yield row

query = """
prepare insert_query(integer, real, integer) as
insert into donor_this_month_temp
(donor, points, team_rank)
values ($1, $2, $3);
"""
cursor.execute(query);

query = """
select distinct on (d.data) u.data
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
order by d.data desc
limit 1;
"""
cursor.execute(query)
batch = cursor.fetchall()[0][0]
#print batch

query = """
select d0.usuario,
   d0.pontos_0 - coalesce(d1.points, 0) as points, d0.n_time
from donors_production_temp as d0
left outer join union_monthly_rank(%s) as d1
   on d0.usuario = d1.donor
inner join usuarios_indice as ui
   on ui.usuario_serial = d0.usuario
order by n_time, points desc;
"""

cursor.execute(query, (batch,))
rs = fetchsome(cursor)

team0 = -1
for (donor, points, team) in rs:
   if team == team0: rank += 1
   else: rank = 1
   insert.execute("execute insert_query(%s, %s, %s)", (donor, points, rank))
   team0 = team
      
connection.commit()
connection.close()

