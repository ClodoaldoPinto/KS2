-- -------------------------------------------------------------------
DROP FUNCTION insert_team_active_members_history(integer, integer, integer);

CREATE OR REPLACE FUNCTION batch_number(interval)
  RETURNS integer AS
$BODY$
select data_serial
from datas
where
	have_data
	and
	data <= (select max(data) from datas) - $1
order by data desc
limit 1
$BODY$
  LANGUAGE sql IMMUTABLE
  COST 100;
ALTER FUNCTION batch_number(interval) OWNER TO kakaostats;
--------------------------------------------------------
CREATE OR REPLACE FUNCTION datas_last_batch_of_each_day()
  RETURNS SETOF datas AS
$BODY$
select data_serial, data, have_data
from datas d
where
	have_data
	and
	data = (
		select max(data)
		from datas
		where
			date_trunc('day', data) =
			date_trunc('day', d.data)
		)
;
$BODY$
  LANGUAGE sql STABLE
  COST 100
  ROWS 1000;
ALTER FUNCTION datas_last_batch_of_each_day() OWNER TO kakaostats;
-------------------------------------------------------------
-- Function: update_donors_rank_temp()

 DROP FUNCTION update_donors_rank_temp();

CREATE OR REPLACE FUNCTION update_donors_rank_temp()
  RETURNS void AS
$BODY$
declare
bn_3_hours constant integer := batch_number('3 hours'::interval);
bn_1_day constant integer := batch_number('1 day'::interval);
bn_7_days constant integer := batch_number('7 days'::interval);
bn_50_days constant integer := batch_number('50 days'::interval);
bn_14_days constant integer := batch_number('14 days 3 hours'::interval);
bn_last constant integer := (select data_serial from datas order by data desc limit 1);
bn_dmonth constant integer := (
select data_serial
        from datas
        where
date_trunc('day', data) = date_trunc('day',
(data + interval '1 month')::date -
extract('day' from data + interval '1 month')::integer
)
and
date_trunc('month', data) < date_trunc('month', current_date at time zone 'utc')
order by data desc
limit 1
);

begin
execute format('
insert into donors_production_temp (
    usuario,
    n_time,
    pontos_0,
    pontos_24,
    pontos_7,
    pontos_up,
    active,
    "new",
    pontos_month,
    rank_0,
    rank_0_time,
    rank_24,
    rank_24_time,
    rank_7,
    rank_7_time,
    rank_30,
    rank_30_time,
    rank_month,
    rank_month_time
)
select usuario, n_time,
    pontos_0,
    pontos_24,
    pontos_7,
    pontos_up,
    active,
    "new",
    pontos_month,
    rank() over (order by pontos_0 desc, pontos_7 desc, pontos_24 desc) as rank_0,
    rank() over (partition by n_time order by pontos_0 desc, pontos_7 desc, pontos_24 desc) as rank_0_time,
    rank() over (order by pontos_0 + (pontos_7 / 7) desc, pontos_0 desc) as rank_24,
    rank() over (partition by n_time order by pontos_0 + (pontos_7 / 7) desc, pontos_0 desc) as rank_24_time,
    rank() over (order by pontos_0 + pontos_7 desc, pontos_0 desc) as rank_7,
    rank() over (partition by n_time order by pontos_0 + pontos_7 desc, pontos_0 desc) as rank_7_time,
    rank() over (order by pontos_0 + (pontos_7 * 30 / 7) desc, pontos_0 desc) as rank_30,
    rank() over (partition by n_time order by pontos_0 + (pontos_7 * 30 / 7) desc, pontos_0 desc) as rank_30_time,
    rank() over (order by pontos_month desc, pontos_0 desc) as rank_month,
    rank() over (partition by n_time order by pontos_month desc, pontos_0 desc) as rank_month_time
from (
    select d0.usuario, usuarios_indice.n_time,
        d0.pontos as pontos_0,
        d0.pontos - coalesce (d1.pontos, 0) as pontos_24,
        d0.pontos - coalesce (d7.pontos, 0) as pontos_7,
        d0.pontos - coalesce (dup.pontos, 0) as pontos_up,
        d0.pontos > coalesce (d50.pontos, 0) as active,
        d0.pontos > coalesce (d14.pontos, 0) and coalesce(d14.pontos, 0) < 1 as "new",
        d0.pontos - coalesce (dmonth.pontos, 0) as pontos_month
    from usuarios as d0
      left outer join usuarios as dup on d0.usuario = dup.usuario and dup.data = %2$s
      left outer join usuarios as d1 on d0.usuario = d1.usuario and d1.data = %3$s
      left outer join usuarios as d7 on d0.usuario = d7.usuario and d7.data = %4$s
      left outer join usuarios as d50 on d0.usuario = d50.usuario and d50.data = %5$s
      left outer join usuarios as d14 on d0.usuario = d14.usuario and d14.data = %6$s
      left outer join usuarios as dmonth on d0.usuario = dmonth.usuario and dmonth.data = %7$s
      inner join usuarios_indice on d0.usuario = usuario_serial
    where
d0.data = %1$s
) sq '
, bn_last, bn_3_hours, bn_1_day, bn_7_days, bn_50_days, bn_14_days, bn_dmonth)
;
end
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION update_donors_rank_temp() OWNER TO kakaostats;
-------------------------------------------------------------------
-- Function: insert_team_active_members_history()

-- DROP FUNCTION insert_team_active_members_history();

CREATE OR REPLACE FUNCTION insert_team_active_members_history()
  RETURNS void AS
$BODY$

declare par record;
begin

for par in 
    with datas as (
        select *
        from datas
        where have_data
    ), d0 as (
        select max(data)::date as data
        from datas
    ), d8 as (
        select max(data) "data"
        from datas d
        where
            data >= (select data from d0) - interval '8 weeks'
            and
            data < (select data from d0)
        group by date_trunc('day', data)
    ), par as (
        select
            d0.data as d0,
            max(d1.data) as d1
        from d8 d0
        inner join d8 d1 on
            d1.data <= d0.data - interval '50 days'
        group by d0
    ), team_history_batch as (
        select distinct serial_date as batch
        from team_active_members_history
        where team_number = 0
    )
    select d0.data_serial as b0, d1.data_serial as b1
    from par p
    inner join datas d0 on p.d0 = d0.data
    inner join datas d1 on p.d1 = d1.data
    where d0.data_serial not in (select batch from team_history_batch)
    order by p.d0 desc
loop
    execute format($f$
        insert into team_active_members_history
        (team_number, active_members, serial_date)
        select n_time, active, %2$s
        from (
            select
                n_time,
                count(*) as active
            from usuarios u0
            left outer join usuarios u50 on
                u0.usuario = u50.usuario
                and
                u50.data = %1$s
            inner join usuarios_indice ui on u0.usuario = ui.usuario_serial
            where
                u0.data = %2$s
                and
                u0.pontos > coalesce(u50.pontos, 0)
            group by n_time
            order by n_time
        ) s
        where active > 0
    $f$, par.b1, par.b0);
end loop;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION insert_team_active_members_history()
  OWNER TO kakaostats;
--------------------------------------------------------------------------
create or replace function db_feed() returns void as
$body$
declare
batch integer;
begin

insert into datas (data)
select last_date
from last_date_temp
;

select max(data_serial) into batch from datas;

insert into times_indice (n_time)
    select n_time from times_temp
    where pontos > 0
    except
    select n_time from times_indice
;

update times_indice
    set time_nome = times_temp.time_nome
    from times_temp
    where
        times_indice.n_time = times_temp.n_time
        and
        times_indice.time_nome != times_temp.time_nome
;

insert into times (data, n_time, pontos, wus)
select
    batch as data_serial,
    times_indice.n_time,
    pontos,
    wus
from times_temp inner join times_indice
    on times_temp.n_time = times_indice.n_time
where times_temp.pontos > 0
order by data_serial, times_indice.n_time
;

insert into usuarios_indice (usuario_nome, n_time)
select usuario, n_time from usuarios_temp
where pontos > 0
except
select usuario_nome, n_time from usuarios_indice
;

execute format('
create table usuarios_%1$s
    (like usuarios including constraints including defaults)
', batch);

execute format('
alter table usuarios_%1$s add constraint b%1$s check (data = %1$s)
', batch);

execute format('
insert into usuarios_%1$s (data, usuario, pontos, wus)
select
    %1$s as data,
    ui.usuario_serial as usuario,
    sum(pontos) as pontos,
    sum(wus) as wus
from usuarios_temp as ut inner join usuarios_indice as ui
    on ut.usuario = ui.usuario_nome and ut.n_time = ui.n_time
where ut.pontos > 0
group by data, ui.usuario_serial
order by data, ui.usuario_serial
', batch);

execute format('
alter table usuarios_%1$s
    add constraint fk_usuarios_%1$s foreign key (data) references datas (data_serial)
', batch);

execute format('
create unique index ndx_usuarios_%1$s on usuarios_%1$s (usuario)
', batch);

execute format('
alter table usuarios_%1$s inherit usuarios
', batch);

execute format('
analyze usuarios_%1$s
', batch);

end;
$body$
  language plpgsql volatile
  cost 100;
alter function db_feed() owner to kakaostats;
-- --------------------------------------------------
CREATE OR REPLACE FUNCTION select_donors_data(integer)
  RETURNS SETOF integer AS
$BODY$
declare
batch int := (
	select data_serial from datas
	where have_data and
		data >= (select max(data) from datas)
			- (($1::text || ' week')::interval)
	order by data asc limit 1
);
begin
return query execute '
select usuario
from usuarios
where data = $1
' using batch;
return;
end
;$BODY$
  LANGUAGE plpgsql STABLE STRICT
  COST 100
  ROWS 1000;
ALTER FUNCTION select_donors_data(integer)
  OWNER TO kakaostats;
-- -------------------------------------------------------
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
-- ---------------------------------------------------------
DROP FUNCTION insert_donor_milestones(integer, integer, integer);
-- -------------------------------------------------------------
-- Function: update_donor_yearly()

-- DROP FUNCTION update_donor_yearly();

CREATE OR REPLACE FUNCTION update_donor_yearly()
  RETURNS void AS
$BODY$
import psycopg2 as db
import sys
sys.path.append("/fahstats/scripts/python")
from setup import connStr

connection = db.connect(connStr["backend"])
cursor = connection.cursor()
update = connection.cursor()

def fetchsome(cursor, chunk=50000):
   while True:
      rs = cursor.fetchmany(chunk)
      if not rs: break
      for row in rs: yield row

query = """
select
   extract(day from current_timestamp)::integer,
   extract(hour from current_timestamp)::integer;
"""
cursor.execute(query)
day, hour = cursor.fetchall()[0]

if day != 1 or hour < 1 or hour > 3:
   connection.close()
   return

query = """
prepare update_query(integer, smallint, real, integer, integer, smallint) as
select update_donor_yearly($1, $2, $3, $4, $5, $6)
"""
cursor.execute(query);

query = """
select distinct extract(year from um.data)::integer,
   extract(month from um.data)::integer, um.data_serial
from (
select distinct d.data, d.data_serial
from usuarios as u
inner join datas as d on u.data = d.data_serial
where
   u.data = (
      select data_serial
      from datas
      where date_trunc('day', data) = date_trunc('day', d.data)
      order by data desc limit 1
      )
   and
   date_trunc('month', d.data) < date_trunc('month', (select last_date from last_date) at time zone 'utc')
   and
   date_trunc('day', d.data) = (
      select date_trunc('day', data)
      from datas
      where date_trunc('month', data) = date_trunc('month', d.data)
      order by data desc limit 1
      )
union
select distinct d.data, d.data_serial
from donor_work_old as dold
inner join datas as d on d.data_serial = dold.data
) as um
order by extract(year from um.data)::integer desc, extract(month from um.data)::integer desc
"""
cursor.execute(query)
months = cursor.fetchall()
#print months

query_dm = """
select year, months
from donor_yearly_fill
"""

query = """
select d0.donor,
   d0.points - coalesce(d1.points, 0) as points, n_time
from union_monthly_rank(%s) as d0
left outer join union_monthly_rank(%s) as d1
   on d0.donor = d1.donor
inner join usuarios_indice as ui
   on ui.usuario_serial = d0.donor
where d0.points - coalesce(d1.points, 0) > 0
order by points desc
;
"""

for i, (year, month, batch) in enumerate(months[:-1]):
   if i > 1000: break
   cursor.execute(query_dm)
   dm = dict(cursor.fetchall())
   #print 'dm:', dm
   if year in dm:
      if month in dm[year]:
         continue
      update.execute(
         "update donor_yearly_fill set months[array_upper(months, 1) +1] = %s where year = %s",
         (month, year))
   else:
      update.execute("insert into donor_yearly_fill values(%s, array[%s])", (year, month))
   #print i, year, month, batch, months[i +1]
   cursor.execute(query, (batch, months[i +1][2]))
   #print 'fim execute query rsi'
   rsi = fetchsome(cursor)
   project_rank = 0
   team_rank = dict()
   for (donor, points, team) in rsi:
      project_rank += 1
      team_rank[team] = team_rank.get(team, 0) + 1
      update.execute("execute update_query(%s, %s, %s, %s, %s, %s)",
                     (donor, year, points, team_rank[team], project_rank, month))
   connection.commit()

connection.close()
$BODY$
  LANGUAGE plpythonu VOLATILE STRICT
  COST 100;
ALTER FUNCTION update_donor_yearly()
  OWNER TO kakaostats;
-- ------------------------------------------------------------------
-- Function: union_monthly_rank(integer)

-- DROP FUNCTION union_monthly_rank(integer);

CREATE OR REPLACE FUNCTION union_monthly_rank(integer)
  RETURNS SETOF type_monthly_rank AS
$BODY$select usuario, pontos, data
from usuarios
where data = $1
union
select usuario, pontos, data
from donor_work_old
where data = $1
$BODY$
  LANGUAGE sql STABLE STRICT
  COST 100
  ROWS 1000;
ALTER FUNCTION union_monthly_rank(integer)
  OWNER TO kakaostats;
------------------------------------------------------------------

create table usuarios_empty_fk (data integer unique check(false));
alter table usuarios add foreign key (data) references usuarios_empty_fk(data);
grant select on usuarios to "phpUser";
alter table donor_work_old add foreign key (data) references usuarios_empty_fk(data);
-- --------------------------------------------------------------
-- Function: delete_old()

-- DROP FUNCTION delete_old();

CREATE OR REPLACE FUNCTION delete_old()
  RETURNS void AS
$BODY$declare
d0 timestamp with time zone;
d15 timestamp with time zone;
d8w timestamp with time zone;
d1a timestamp with time zone;
batch_id integer;
rday record;
begin

if extract(hour from current_timestamp)::integer between 1 and 23 then
    return;
end if;

d0 := (select max(data) from datas where have_data);
d15 := d0 - interval '15 days';
d8w := d0 - interval '8 weeks 1 day';
d1a := d0 - interval '1 year';

create temporary table batch as
    with dias as (
        select distinct on (dia)
            d.data::date as dia,
            d.data,
            data_serial
        from datas d
        where have_data
        order by dia, d.data desc
    ), meses as (
        select distinct on (mes)
            date_trunc('month', dias.data) as mes,
            dias.data,
            data_serial
        from dias
        order by mes, dias.data desc
    )
    select data_serial as batch, d.data
    from datas d
    where
        data_serial not in (
            select data_serial
            from meses
            where meses.data between d1a and d8w
            union
            select data_serial
            from dias
            where dias.data between d8w and d15
        )
        and
        d.data < d15
        and have_data
;
-- teams ------------------------------------------

delete from times
where data in (
    select batch
    from batch
    )
;

-- donors ------------------------------------------
for batch_id in
select batch from batch
loop
    execute format('drop table usuarios_%s', batch_id);
    update datas set have_data = false where data_serial = batch_id;
end loop;

for batch_id in
    select data_serial
    from datas
    where data < d8w and have_data
loop
    execute format('alter table usuarios_%s no inherit usuarios, inherit donor_work_old', batch_id);
    update datas set have_data = false where data_serial = batch_id;
end loop;

drop table batch;
return;
end;$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION delete_old()
  OWNER TO kakaostats;
-- -------------------------------------------------------
alter database fahstats rename to folding;
