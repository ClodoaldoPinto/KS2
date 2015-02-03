import psycopg

def fetchsome(cursor, arraysize=5000):
  ''' A generator that simplifies the use of fetchmany '''
  while True:
    results = cursor.fetchmany(arraysize)
    if not results: break
    for result in results:
      yield result

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
serial_dates = (fetchsome(cursor))

query = """
select distinct serial_date
from team_active_members_history;"""

cursor_2 = db.cursor()
cursor_2.execute(query)
l = (d[0] for d in fetchsome(cursor_2))
l = dict.fromkeys(l)

sd = (d for d in serial_dates if d[0] not in l)

query = 'select n_time from times_indice;'
cursor_3 = db.cursor()
cursor_3.execute(query)
team_active_users = (team[0] for team in fetchsome(cursor_3))
team_active_users = dict.fromkeys(team_active_users, 0)


cursor_4 = db.cursor()
cursor_5 = db.cursor()

for d1, d0 in sd:

  print d1, d0
  query = """
  select u.usuario, u.pontos, ui.n_time
  from usuarios as u
  inner join usuarios_indice as ui
  on u.usuario = ui.usuario_serial
  where u.data = """ + str(d1) + ';'

  cursor_4.execute(query)
  donors_d1 = (fetchsome(cursor_4))

  query = """
  select u.usuario, u.pontos
  from usuarios as u
  where u.data = """ + str(d0) + ';'

  cursor_5.execute(query)
  donors_d0 = dict((donor, points) for donor, points in fetchsome(cursor_5))

  for donor, points, team in donors_d1:
    if points > donors_d0.get(donor, 0):
      team_active_users[team] = team_active_users.setdefault(team, 0) + 1

  for team in team_active_users:
    if team_active_users[team] > 0:
      query = 'select insert_team_active_members_history(' + \
        str(team) + ',' + str(team_active_users[team]) + ',' + str(d1) + \
        ');'
      ins_cursor.execute(query)
      team_active_users[team] = 0

  print len(donors_d0) #del(donors_d0)
  db.commit()


ins_cursor.close()
db.commit()
db.close()

