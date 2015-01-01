import psycopg
import sys


db = psycopg.connect("host=localhost dbname=fahstats")
cursor = db.cursor()
ins_cursor = db.cursor()


query = """
select d1_serial, d0_serial
from select_two_serial_dates_x_days_last_batch(14) as tsd
inner join datas as d on d.data_serial = tsd.d1_serial
where d.data >= (
  select data from datas order by data desc limit 1)
  - '8 weeks'::interval;
"""
cursor.execute(query)
serial_dates = cursor.fetchall()


query = """
select distinct serial_date
from team_active_members_history;"""

cursor.execute(query)
l = [d[0] for d in cursor.fetchall()]
print l,'\n'
l = dict(zip(l, [None for d in l]))
print l

serial_dates = [d for d in serial_dates if d[0] not in l]
print
print serial_dates
del(l)

query = 'select n_time from times_indice;'
cursor.execute(query)
team_active_users = [team[0] for team in cursor.fetchall()]
team_active_users = dict( \
        zip(team_active_users, [0 for team in team_active_users]))


for d1, d0 in serial_dates:

  query = """
  select u.usuario, u.pontos, ui.n_time
  from usuarios as u
  inner join usuarios_indice as ui
  on u.usuario = ui.usuario_serial
  where ui.n_time in (13802, 36120) and
    u.data = """ + str(d1) + ';'

  cursor.execute(query)
  donors_d1 = cursor.fetchall()

  query = """
  select u.usuario, u.pontos
  from usuarios as u
  inner join usuarios_indice as ui
  on u.usuario = ui.usuario_serial
  where ui.n_time in (13802, 36120) and
    u.data = """ + str(d0) + ';'

  cursor.execute(query)
  donors_d0 = dict([(donor, points) for donor, points in cursor.fetchall()])

  for donor, points, team in donors_d1:
    if points > donors_d0.get(donor, 0):
      team_active_users[team] = team_active_users.setdefault(team, 0) + 1

  print 13802, d1, team_active_users[13802]
  for team in team_active_users:
    if team_active_users[team] > 0:
      query = 'select insert_team_active_members_history(' + \
        str(team) + ',' + str(team_active_users[team]) + ',' + str(d1) + \
        ');'
      ins_cursor.execute(query)
      team_active_users[team] = 0
  db.commit()


cursor.close()
ins_cursor.close()
db.commit()
db.close()

