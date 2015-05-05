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
    team_radar = True,
    team_size = True,
    donor = True
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
    inner join times t on d.data_serial = t.data
    where
        n_time = %(team)s
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
    from times t
    inner join datas d on d.data_serial = t.data
    where
        n_time = %(team)s
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

team_query = """\
select time_nome as team_name
from times_indice
where n_time = %(team)s
;"""

@app.route("/team-history")
def team_history():

    d = request.args

    team = d.get('team', -1, int)
    if team < 0: return ''

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['daily'] = {
        'query': daily_query,
        'args': {'team': team}
        }
    queries['team'] = {
        'query': team_query,
        'args': {'team': team}
        }

    rs = get_rs(queries)
    team_name=rs['team'][0]['team_name']
    del rs['team']

    history_json = quote_plus(json.dumps(
        [[int(d['points']), d['wus'], d['day'], d['dow']] for d in rs['daily'][:-1]]
        , separators=(',',':')))

    return render_template(
        'team-history.html',
        team_name=team_name,
        n_time=team,
        menu=menu,
        rs = rs,
        history_json=history_json
        )
