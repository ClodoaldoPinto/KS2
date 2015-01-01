# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request
from db_connection import get_rs
from paginador import paginador
from psycopg2.extensions import AsIs
from app import app

menu = menu_dict.menu.copy()
menu['anchors_all_teams'] = True

order = {
    1: "donor",
    2: "rank_0",
    3: "rank_24_team",
    4: "rank_7_team",
    5: "rank_30_team",
    6: "rank_0",
    7: "rank_24",
    8: "rank_7",
    9: "rank_30",
    10: "pontos_up desc, rank_0_team",
    11: "pontos_24 desc, rank_0_team",
    12: "pontos_7 desc, rank_0_team",
    13: "pontos_0 desc, rank_0_team",
    14: "time_nome, rank_0"
    }

query_data = """\
select to_char (last_date, 'YYYY-MM-DD HH24:MI:SS') as date,
  (select extract(epoch from "datetime") as unixtimestamp
    from processing_end) as unixtimestamp,
  extract(epoch from(select "datetime" from processing_end) +
  '3 hours 3 minutes'::interval - current_timestamp(0)
   )::bigint * 1000 as ttu
  from last_date
;"""

query_count_search = """\
select
    "all",
    active,
    "new",
    "all" - active as inactive
from (
    select
        count(*) as "all",
        count(active or null) as active,
        count("new" or null) as "new"
    from donors_production t
    inner join usuarios_indice d on d.usuario_serial = t.usuario
    where
        lower(d.usuario_nome) like lower(%(search)s)
) s
;"""

query_count_no_search = """\
select
    sum(total_members) as all,
    sum(new_members) as "new",
    sum(active_members) as active,
    sum(total_members) - sum(active_members) as inactive
from teams_production
where n_time != -1
;"""

query_donors = """\
select
    d.usuario_nome as donor,
    ti.n_time,
    ti.time_nome as team,
    d.usuario_serial as n_member,
    rank_0, rank_24, rank_7, rank_30,
    rank_0_time as rank_0_team,
    rank_24_time as rank_24_team,
    rank_7_time as rank_7_team,
    rank_30_time as rank_30_team,
    pontos_0,
    pontos_24,
    pontos_7,
    pontos_up
from donors_production t
inner join usuarios_indice d on d.usuario_serial = t.usuario
inner join times_indice ti on d.n_time = ti.n_time
where
    %(activity)s
    and
    case when %(search)s != '%%' then
        lower(d.usuario_nome) like lower(%(search)s)
        else true end
order by %(order)s
limit %(row_count)s offset %(offset)s
;"""

activity_filter_option = {
    'all': 'true',
    'inactive': 'not active',
    'active': 'active',
    'new': 'new'
}

@app.route("/donors")
def donors():

    d = request.args
    
    order_opt = d.get('order', 6, int)
    if order_opt < 1 or order_opt > 13: order_opt = 6

    search = d.get('search', '')
    
    page = abs(d.get('page', 1, int))
    if page < 1:
        page = 1

    offset = (page - 1) * config.row_count
    
    activity = (d.get('activity', 'active')).lower()
    if activity not in activity_filter_option or activity == 'active':
        activity = None
    activity_filter = activity_filter_option.get(activity, activity_filter_option['active'])
    
    small_thousands = request.cookies.get('smallThousands', 'checked')
    
    queries = dict()
    queries['data'] = {'query': query_data}
    queries['donors'] = {
        'query': query_donors,
        'args': {
            'search': '%%%s%%' % search,
            'order': AsIs(order[order_opt]),
            'offset': offset,
            'row_count': config.row_count,
            'activity': AsIs(activity_filter)
            }
        }
    queries['count'] = {
        'query': query_count_no_search if not search else query_count_search,
        'args': {'search': '%%%s%%' % search}
        }
    
    rs = get_rs(queries)
    
    #return repr(rs['donors'])
    
    rs['count'] = rs['count'][0]
    n_members = rs['count'][activity if activity else 'active']
    
    indice_paginas = paginador(n_members + 1, page)

    return render_template(
        'donors.html',
        menu=menu,
        rs=rs,
        offset=offset,
        indice_paginas=indice_paginas,
        search=search or None,
        order_opt=order_opt,
        page=page,
        small_thousands=small_thousands,
        activity=activity,
    )
