# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request, json
from db_connection import get_rs
from app import app
from urllib import quote_plus

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
    donor_log = True,
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

daily_query = """\
with d_min as (
    select min(d.data)::date as data
    from datas d
    inner join usuarios u on d.data_serial = u.data
    where
        usuario = %(donor)s
        and
        d.data >= (
            select
                max(data)
                - interval '7 weeks 1 day'
                - extract(dow from max(data)) * interval '1 day'
            from datas
        )
)
select
    coalesce(points, 0) points,
    coalesce(wus, 0) wus,
    to_char(gd, 'YYYY-MM-DD') as "day",
    extract(isodow from gd)::integer as dow,
    yearweek(gd) as yw
from (
    select
        pontos - lead(pontos, 1, 0::real) over w as points,
        wus - lead(wus, 1, 0) over w as wus,
        d.data::date
    from usuarios u
    inner join datas d on d.data_serial = u.data
    where
        usuario = %(donor)s
        and
        d.data = any (
            select sq.data
            from (
                select
                    data::date as "day",
                    max(data) as data
                from datas
                where
                    data >= (select data from d_min)
                    and
                    have_data
                group by day
                ) sq
            )
    window w as (order by d.data desc)
) ss right join (
    select gd::date gd
    from
    generate_series(
        (select data from d_min),
        (select max(data) from datas),
        '1 day'
    ) gs(gd)
) gs on gs.gd = ss.data
order by day
offset 2
;"""

donor_query = """\
select n_time, usuario_nome, usuario_serial as donor
from usuarios_indice
where usuario_serial = %(donor)s
;"""

@app.route("/donor-history")
def donor_history():

    d = request.args

    donor = d.get('donor', -1, int)
    if donor < 1: return ''

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['daily'] = {
        'query': daily_query,
        'args': {'donor': donor}
        }
    queries['donor'] = {
        'query': donor_query,
        'args': {'donor': donor}
        }

    rs = get_rs(queries)

    history_json = quote_plus(json.dumps(
        [[int(d['points']), d['wus'], d['day'], d['dow']] for d in rs['daily'][:-1]]
        , separators=(',',':')))

    return render_template(
        'donor-history.html',
        n_time=rs['donor'][0]['n_time'],
        donor=donor,
        menu=menu,
        rs = rs,
        history_json=history_json
        )
