# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request
from db_connection import get_rs
from psycopg2.extensions import AsIs
from app import app

menu = menu_dict.menu.copy()
menu.update(
    anchors_all_donors = True,
    anchors_all_teams = True,
    team = True,
    team_members = True,
    team_history = True,
    team_radar = True,
    team_size = True,
    donor = True,
    donor_history = True,
    donor_radar = True
)

query_data = """
select to_char (last_date, 'YYYY-MM-DD HH24:MI:SS') as date,
  (select extract(epoch from "datetime") as unixtimestamp
    from processing_end) as unixtimestamp,
  extract(epoch from(select "datetime" from processing_end) +
  '3 hours 3 minutes'::interval - current_timestamp(0)
   )::bigint * 1000 as ttu
  from last_date
;"""

update_query = """\
select
    points,
    wus,
    to_char(data, 'YYYY-MM-DD') as  "day",
    to_char(data, 'HH24:MI') as "time"
from (
    select
        d.data,
        pontos - lead(pontos, 1, 0::real) over w as points,
        wus - lead(wus, 1, 0) over w as wus
    from usuarios u
    inner join datas d on d.data_serial = u.data
    where
      usuario = %(donor)s
      and
      d.data > (select max(data) - interval '15 days' from datas)
      and
      d.have_data
    window w as (order by d.data desc)
    ) ss
where
    points is not null and points != 0
    and
    data > (select max(data) - interval '14 days' from datas)
order by day desc, "time" desc
;"""

donor_query = """\
select n_time, usuario_nome, usuario_serial as donor
from usuarios_indice
where usuario_serial = %(donor)s
;"""

@app.route("/donor-log")
def donor_log():

    d = request.args

    donor = d.get('donor', -1, int)
    if donor < 1: return ''

    small_thousands = request.cookies.get('smallThousands', 'checked')

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['update'] = {
        'query': update_query,
        'args': {'donor': donor}
        }
    queries['donor'] = {
        'query': donor_query,
        'args': {'donor': donor}
        }

    rs = get_rs(queries)

    return render_template(
        'donor-log.html',
        n_time=rs['donor'][0]['n_time'],
        donor=donor,
        menu=menu,
        rs = rs
        )
