# -*- coding: utf-8 -*-
import config, menu_dict
from flask import render_template, request
from db_connection import get_rs
from paginador import paginador
from psycopg2.extensions import AsIs
from app import app

menu = menu_dict.menu.copy()
menu['anchors_all_donors'] = True

order = {
    1: "active_members desc, rank_0",
    2: "time_nome, rank_0",
    3: "rank_0",
    4: "rank_24, rank_0",
    5: "rank_7, rank_0",
    6: "rank_30, rank_0",
    7: "pontos_24 desc, rank_0",
    8: "pontos_7 desc, rank_0",
    9: "pontos_7 / active_members desc, rank_0",
    10: "pontos_0 desc",
    11: "new_members desc, rank_0",
    12: "pontos_up desc, rank_0"
    }

query_data = """
select to_char (last_date, 'YYYY-MM-DD HH24:MI:SS') as date,
  (select extract(epoch from "datetime") as unixtimestamp
    from processing_end) as unixtimestamp,
  extract(epoch from(select "datetime" from processing_end) +
  '3 hours 3 minutes'::interval - current_timestamp(0)
   )::bigint * 1000 as ttu
  from last_date
;"""

query_times = """
select
  active_members,
  at.n_time,
  rank_0, rank_24, rank_7, rank_30,
  pontos_0 / 1000 as pontos_0,
  pontos_24,
  pontos_7,
  pontos_up,
  ti.time_nome,
  new_members
from teams_production as at
inner join times_indice as ti on at.n_time = ti.n_time
where
  active
  and
  active_members > 0
  and
  case when %(search)s != '%%' then
        lower(ti.time_nome) like lower(%(search)s)
        else true end
order by ti.n_time != -1, ti.n_time != 0, %(order)s
limit %(row_count)s offset %(offset)s
;"""

query_count = """
select count(*) as n_times
from teams_production as at
inner join times_indice as ti on at.n_time = ti.n_time
where
  active
  and
  active_members > 0
  and
  case when %(search)s != '%%' then
        lower(ti.time_nome) like lower(%(search)s)
        else true end
;"""

@app.route("/")
def index():

    d = request.args

    order_opt = d.get('order', 3, int)
    if order_opt < 1 or order_opt > 12: order_opt = 3

    search = d.get('search', '')

    page = abs(d.get('page', 1, int))
    if page < 1:
        page = 1

    small_thousands = request.cookies.get('smallThousands', 'checked')

    offset = (page - 1) * config.row_count

    queries = dict()
    queries['data'] = {'query': query_data}
    queries['times'] = {
        'query': query_times,
        'args': {
            'search': '%%%s%%' % search,
            'order': AsIs(order[order_opt]),
            'offset': offset,
            'row_count': config.row_count
            }
        }
    queries['count'] = {
        'query': query_count,
        'args': {'search': '%%%s%%' % search}
        }
    rs = get_rs(queries)

    n_times = rs['count'][0]['n_times']
    indice_paginas = paginador(n_times, page)

    return render_template(
        'index.html',
        menu=menu,
        rs = rs,
        offset = offset,
        indice_paginas = indice_paginas,
        search = search or None,
        order_opt = order_opt,
        page = page,
        small_thousands = small_thousands,
        n_times = n_times - 1
        )
