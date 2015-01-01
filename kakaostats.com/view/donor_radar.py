# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request, json
from db_connection import get_rs
from app import app
from urllib import quote_plus

menu = menu_dict.menu.copy()
menu.update (
    anchors_all_donors = True,
    anchors_all_teams = True,
    team = True,
    team_members = True,
    team_history = True,
    team_radar = True,
    team_size = True,
    donor = True,
    donor_history = True,
    donor_log = True
)

query_radar = """\
with u0 as (
    select
        usuario,
        rank_0,
        rank_0_time,
        pontos_0,
        pontos_up,
        pontos_7,
        pontos_24,
        n_time
    from donors_production
    where usuario = %(donor)s
)
select
    usuario_nome as donor_name,
    days,
    "date",
    usuario as donor_number,
    rank_0,
    rank_0_time,
    pontos_0::integer,
    pontos_up::integer,
    pontos_7::integer,
    pontos_24::integer,
    pontos_0_diff::integer,
    pontos_up_diff::integer,
    pontos_7_diff::integer,
    pontos_24_diff::integer
from (
    select
        0 as days,
        '' as "date",
        usuario,
        rank_0,
        rank_0_time,
        pontos_0,
        pontos_up,
        pontos_7,
        pontos_24,
        0 as pontos_0_diff,
        0 as pontos_up_diff,
        0 as pontos_7_diff,
        0 as pontos_24_diff
    from u0
    union
    select
        ((u0.pontos_0 - u1.pontos_0) * 7 / (u1.pontos_7 - u0.pontos_7))::integer,
        to_char(
            (select last_date from last_date) + case
                when
                    (u0.pontos_0 - u1.pontos_0) / (u1.pontos_7 - u0.pontos_7) > 421200
                    then null else
                    (((u0.pontos_0 - u1.pontos_0) / (u1.pontos_7 - u0.pontos_7)
                    )::text || ' week')::interval
                end
            , 'YYYY-MM-DD HH24:MI'),
        u1.usuario,
        u1.rank_0,
        u1.rank_0_time,
        u1.pontos_0,
        u1.pontos_up,
        u1.pontos_7,
        u1.pontos_24,
        u1.pontos_0 - u0.pontos_0,
        u1.pontos_up - u0.pontos_up,
        u1.pontos_7 - u0.pontos_7,
        u1.pontos_24 - u0.pontos_24
    from donors_production u1
    inner join u0 on true
    where active
        and u1.n_time = (select n_time from u0)
        and (
        (
            u0.pontos_7 < u1.pontos_7
            and
            u0.pontos_0 > u1.pontos_0
        )
        or
        (
            u0.pontos_7 > u1.pontos_7
            and
            u0.pontos_0 < u1.pontos_0
        )
    )
) ss
inner join usuarios_indice as ui on ss.usuario = ui.usuario_serial
where days <= 999
order by
    ui.usuario_serial = %(donor)s desc,
    days, pontos_7, pontos_0
limit 200
;"""

query_data = """\
select to_char (last_date, 'YYYY-MM-DD HH24:MI:SS') as date,
  (select extract(epoch from "datetime") as unixtimestamp
    from processing_end) as unixtimestamp,
  extract(epoch from(select "datetime" from processing_end) +
  '3 hours 3 minutes'::interval - current_timestamp(0)
   )::bigint * 1000 as ttu
  from last_date
;"""

donor_query = """\
select n_time, usuario_nome, usuario_serial as donor
from usuarios_indice
where usuario_serial = %(donor)s
;"""

@app.route("/donor-radar")
def donor_radar():

    d = request.args

    donor = d.get('donor', -1, int)
    if donor < 1: return ''

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['radar'] = {
        'query': query_radar,
        'args': {'donor': donor}
        }
    queries['donor'] = {
        'query': donor_query,
        'args': {'donor': donor}
        }

    rs = get_rs(queries)

    radar_json = quote_plus(json.dumps([
            [
                d['donor_name'],
                d['days'],
                d['pontos_0'],
                d['pontos_7']
            ] for d in rs['radar'][:11]
        ], separators=(',',':')))

    return render_template(
        'donor-radar.html',
        n_time=rs['donor'][0]['n_time'],
        donor=donor,
        menu=menu,
        rs = rs,
        radar_json=radar_json
        )
