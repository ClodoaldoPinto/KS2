import psycopg
import sys


db = psycopg.connect("host=localhost dbname=fahstats")
cursor = db.cursor()


query = """
select d1_serial, d0_serial
from select_two_consecutive_serial_dates() as tcsd
inner join datas as d on d.data_serial = tcsd.d1_serial
where d.data >= (
  select data from datas order by data desc limit 1)
  - '7 weeks'::interval;
"""
cursor.execute(query)
serial_dates = cursor.fetchall()


query = """
select distinct serial_date
from donor_milestones;"""

cursor.execute(query)
l = [d[0] for d in cursor.fetchall()]
print l,'\n'
l = dict(zip(l, [None for d in l]))
print l

serial_dates = [d for d in serial_dates if d[0] not in l]
print
print serial_dates
del(l)


query = """
select milestone_ref, milestone_points
from donor_milestones_ref
order by milestone_points
"""

cursor.execute(query)
milestone_table = [(milestone_ref, milestone_points) \
  for milestone_ref, milestone_points in cursor.fetchall()]


for d1, d0 in serial_dates:

  query = """
  select u.usuario, u.pontos
  from usuarios as u
  where u.data = """ + str(d1) + ';'
  print query

  cursor.execute(query)
  donors_d1 = cursor.fetchall()

  query = """
  select u.usuario, u.pontos
  from usuarios as u
  where u.data = """ + str(d0) + ';'
  print query

  cursor.execute(query)
  print 'donors_d0 antes'
  donors_d0 = dict([(donor, points) for donor, points in cursor.fetchall()])
  print 'donors_d0 depois'

  for donor, points in donors_d1:
    for milestone_ref, milestone_points in milestone_table:
      if points >= milestone_points and \
         milestone_points > donors_d0.get(donor, 999999999999):
        print d1, donor, points, milestone_points
        query = 'select insert_donor_milestones(' + \
          str(donor) + ',' + str(milestone_ref) + ',' + str(d1) + \
          ');'
        cursor.execute(query)
        break

  db.commit()


cursor.close()
db.commit()
db.close()

