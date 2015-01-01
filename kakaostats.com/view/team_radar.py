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
    team_size = True,
    donor = True,
    team_history = True
)

query_radar = """\
with u0 as (
    select
        n_time,
        rank_0,
        pontos_0,
        pontos_up,
        pontos_7,
        pontos_24
    from teams_production
    where n_time = %(team)s
)
select
    time_nome as team_name,
    days,
    "date",
    ti.n_time,
    rank_0,
    pontos_0,
    pontos_up,
    pontos_7,
    pontos_24,
    pontos_0_diff,
    pontos_up_diff,
    pontos_7_diff,
    pontos_24_diff
from (
    select
        0 as days,
        '' as "date",
        n_time,
        rank_0,
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
        u1.n_time,
        u1.rank_0,
        u1.pontos_0,
        u1.pontos_up,
        u1.pontos_7,
        u1.pontos_24,
        u1.pontos_0 - u0.pontos_0,
        u1.pontos_up - u0.pontos_up,
        u1.pontos_7 - u0.pontos_7,
        u1.pontos_24 - u0.pontos_24
    from teams_production u1
    inner join u0 on true
    where active
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
inner join times_indice as ti on ss.n_time = ti.n_time
where days <= 999
order by
    ti.n_time = %(team)s desc,
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

team_query = """\
select time_nome as team_name
from times_indice
where n_time = %(team)s
;"""

@app.route("/team-radar")
def team_radar():

    d = request.args

    team = d.get('team', -1, int)
    if team < 1: return ''

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['radar'] = {
        'query': query_radar,
        'args': {'team': team}
        }
    queries['team'] = {
        'query': team_query,
        'args': {'team': team}
        }

    rs = get_rs(queries)
    team_name = rs['team'][0]['team_name']
    del rs['team']

    radar_json = quote_plus(json.dumps([
            [
                d['team_name'],
                d['days'],
                d['pontos_0'],
                d['pontos_7']
            ] for d in rs['radar'][:11]
        ], separators=(',',':')))

    return render_template(
        'team-radar.html',
        n_time=team,
        team_name=team_name,
        menu=menu,
        rs = rs,
        radar_json=radar_json
        )
