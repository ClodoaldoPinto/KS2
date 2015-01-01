-- Function: insert_donor_milestones()

-- DROP FUNCTION insert_donor_milestones();

CREATE OR REPLACE FUNCTION insert_donor_milestones()
  RETURNS boolean AS
$BODY$import psycopg2
import sys
sys.path.append("/fahstats/scripts/python")
from setup import connStr

db = psycopg2.connect(connStr["backend"])
cursor = db.cursor()

query = """\
select d1_serial, d0_serial
from select_two_consecutive_serial_dates() as tcsd
inner join datas as d on d.data_serial = tcsd.d1_serial
where d.data >= (select max(data) from datas)
    - '7 weeks'::interval
order by d.data
;"""
cursor.execute(query)
serial_dates = cursor.fetchall()


query = """\
select distinct serial_date
from donor_milestones
;"""

cursor.execute(query)
l = [d[0] for d in cursor.fetchall()]
l = dict(zip(l, [None for d in l]))

serial_dates = [d for d in serial_dates if d[0] not in l]
del(l)

for d1, d0 in serial_dates:

    query = """\
    insert into donor_milestones (donor, serial_date, milestone)
    select u0.usuario, u1.data, milestone_ref
    from usuarios u1
    left outer join usuarios u0 on u0.usuario = u1.usuario
    inner join donor_milestones_ref dmr on
        u1.pontos >= milestone_points
        and
        milestone_points > coalesce(u0.pontos, 0)
    where u1.data = %s and u0.data = %s
    ;""" % (d1, d0)

    cursor.execute(query)

cursor.close()
db.commit()
db.close()
$BODY$
  LANGUAGE plpythonu VOLATILE STRICT
  COST 100;
ALTER FUNCTION insert_donor_milestones() OWNER TO kakaostats;
