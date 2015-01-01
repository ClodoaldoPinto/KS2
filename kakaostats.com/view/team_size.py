# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request, json
from db_connection import get_rs, mogrify
from app import app
from urllib import quote_plus

menu = menu_dict.menu.copy()
menu.update(
    anchors_all_donors = True,
    anchors_all_teams = True,
    team = True,
    team_members = True,
    team_radar = True,
    team_history = True,
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

size_query = """\
with am as (
    select
        active_members,
        data::date as dia
    from
        team_active_members_history tam
        inner
        join datas d on d.data_serial = tam.serial_date
    where team_number = %(team)s
), nm as (
    select
        sum(case when donor is null then 0 else 1 end) as new_members,
        d.data as dia
    from (
            select data::date as data, donor
            from donor_first_wu
        ) dfw
        inner join
        usuarios_indice ui on ui.usuario_serial = dfw.donor and ui.n_time = %(team)s
        right join (
            select date_trunc('day', data) as data
            from datas
            group by 1
        ) d on d.data = dfw.data
    group by dia
), w15 as (
    select (max(data) - '15 weeks'::interval)::date dia
    from datas
)
select
    active_members am,
    new_members nm,
    to_char(s.dia, 'YYYY-MM-DD') as "day",
    extract(isodow from s.dia)::integer as dow,
    yearweek(s.dia) as yw
from (
        select dia::date as dia
        from generate_series(
            least(
                (select min(dia) from nm where dia >= (select dia from w15)),
                (select min(dia) from am where dia >= (select dia from w15))
            ),
            greatest(
                (
                    select max(d.data)
                    from
                        team_active_members_history tamh
                        inner join
                        datas d on d.data_serial = tamh.serial_date
                ),
                (select max(data) from donor_first_wu)
            ),
            '1 day'
        ) s(dia)
    ) s
    left outer join am on s.dia = am.dia
    left outer join nm on s.dia = nm.dia
order by s.dia
;"""

team_query = """\
select time_nome as team_name
from times_indice
where n_time = %(team)s
;"""

@app.route("/team-size")
def team_size():

    d = request.args

    team = d.get('team', -1, int)
    if team < 0: return ''

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['size'] = {
        'query': size_query,
        'args': {'team': team}
        }
    queries['team'] = {
        'query': team_query,
        'args': {'team': team}
        }

    #return '<pre>%s</pre>' % mogrify(queries['size'])

    rs = get_rs(queries)
    team_name=rs['team'][0]['team_name']
    del rs['team']

    history_json = quote_plus(json.dumps(
        [[d['am'], d['nm'], d['day']] for d in rs['size']]
        , separators=(',',':')))

    return render_template(
        'team-size.html',
        team_name=team_name,
        n_time=team,
        menu=menu,
        rs = rs,
        history_json=history_json
        )
