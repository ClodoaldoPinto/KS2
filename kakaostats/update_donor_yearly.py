import psycopg2 as db
import sys
sys.path.append("/fahstats/scripts/python")
from setup import connStr

connection = db.connect(connStr["backend"])
cursor = connection.cursor()
update = connection.cursor()

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

#if day != 1 or hour < 1 or hour > 3:
#   connection.close()
#   return

query = """
prepare update_query(integer, smallint, real, integer, integer, smallint) as
select update_donor_yearly($1, $2, $3, $4, $5, $6)
"""
cursor.execute(query);

query = """
select distinct extract(year from um.data)::integer,
   extract(month from um.data)::integer, um.data_serial
from (
select distinct d.data, d.data_serial
from usuarios as u
inner join datas as d on u.data = d.data_serial
where
   u.data = (
      select data_serial
      from datas
      where date_trunc('day', data) = date_trunc('day', d.data)
      order by data desc limit 1
      )
   and
   date_trunc('month', d.data) < date_trunc('month', (select last_date from last_date) at time zone 'utc')
   and
   date_trunc('day', d.data) = (
      select date_trunc('day', data)
      from datas
      where date_trunc('month', data) = date_trunc('month', d.data)
      order by data desc limit 1
      )
union
select distinct d.data, d.data_serial
from donor_work_old as dold
inner join datas as d on d.data_serial = dold.data
) as um
order by extract(year from um.data)::integer desc, extract(month from um.data)::integer desc
"""
cursor.execute(query)
months = cursor.fetchall()
#print months

query_dm = """
select year, months
from donor_yearly_fill
"""

query = """
select d0.donor,
   d0.points - coalesce(d1.points, 0) as points, n_time
from union_monthly_rank(%s) as d0
left outer join union_monthly_rank(%s) as d1
   on d0.donor = d1.donor
inner join usuarios_indice as ui
   on ui.usuario_serial = d0.donor
where d0.points - coalesce(d1.points, 0) > 0
order by points desc
;
"""

for i, (year, month, batch) in enumerate(months[:-1]):
   if i > 1000: break
   cursor.execute(query_dm)
   dm = dict(cursor.fetchall())
   #print 'dm:', dm
   if year in dm:
      if month in dm[year]:
         continue
      update.execute(
         "update donor_yearly_fill set months[array_upper(months, 1) +1] = %s where year = %s",
         (month, year))
   else:
      update.execute("insert into donor_yearly_fill values(%s, array[%s])", (year, month))
   #print i, year, month, batch, months[i +1]
   cursor.execute(query, (batch, months[i +1][2]))
   #print 'fim execute query rsi'
   rsi = fetchsome(cursor)
   project_rank = 0
   team_rank = dict()
   for (donor, points, team) in rsi:
      project_rank += 1
      team_rank[team] = team_rank.get(team, 0) + 1
      update.execute("execute update_query(%s, %s, %s, %s, %s, %s)",
                     (donor, year, points, team_rank[team], project_rank, month))
   connection.commit()

connection.close()
