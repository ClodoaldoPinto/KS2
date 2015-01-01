import sys
sys.path.append("/fahstats/scripts/python")
from setup import connStr
from psycopg2.extras import RealDictConnection

def fetchsome(cursor, arraysize=50000):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results: break
        for result in results:
            yield result

db = RealDictConnection(connStr["backend"])
cursor = db.cursor()

query = """
select d1_serial as d0, d0_serial as d1
from select_two_serial_dates_x_days_last_batch(50) as tsd
inner join datas as d on d.data_serial = tsd.d1_serial
where d.data >= (
  select max(data) from datas where have_data)
  - '8 weeks'::interval
;"""
cursor.execute(query)
serial_dates = cursor.fetchall()

query = """
select distinct serial_date
from team_active_members_history
where team_number = 0
;"""

cursor.execute(query)
l = [d['serial_date'] for d in cursor.fetchall()]
serial_dates = [d for d in serial_dates if d['d0'] not in l and d['d1'] is not None]
del(l)

for d in serial_dates:

    query = """
    insert into team_active_members_history
    (team_number, active_members, serial_date)
    select team_number, active_members, serial_date
    from (
        select
            count(u0.pontos > coalesce(u1.pontos, 0) or null) as active_members,
            u0.data as serial_date,
            ui.n_time as team_number
        from usuarios u0
        left outer join usuarios u1 on u0.usuario = u1.usuario and u1.data = %s
        inner join usuarios_indice as ui on u0.usuario = ui.usuario_serial
        where u0.data = %s
        group by ui.n_time, u0.data
    ) s
    where active_members > 0
    """ % (d['d1'], d['d0'])

    print query
    #cursor.execute(query)

cursor.close()
db.commit()
db.close()
