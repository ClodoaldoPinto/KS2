explain
with d0 as (
    select data_serial as batch, data
    from datas
    where
        have_data
        and
        data < current_date
    order by data desc
    limit 1
),
d50 as (
    select data_serial as batch
    from datas
    where
        have_data
        and
        data <= (select data from d0) - interval '50 days'
--    order by data
--    limit 1
)
select
    n_time,
    sum(case when u0.wus > coalesce(u50.wus, 0) then 1 else 0 end) as active
from usuarios u0
inner join usuarios u50 on u0.usuario = u50.usuario
left outer join usuarios_indice ui on u0.usuario = ui.usuario_serial
where
    u0.data = (select batch from d0)
    and
    u50.data in (select batch from d50)
    and n_time = 0
group by n_time
order by n_time
;

explain
select n_time, count(*) as active
from usuarios u0
left outer join usuarios u50 on
    u0.usuario = u50.usuario
    and
    u50.data = 23792
inner join usuarios_indice ui on u0.usuario = ui.usuario_serial
where
    u0.data = 24380
    and
    u0.pontos > coalesce(u50.pontos, 0)
    and n_time = 0
group by n_time
order by n_time
;

create or replace function insert_team_active_members_history()
returns void
language plpgsql volatile as $body$

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
        select data
        from datas d
        where
            data between (select data from d0) - interval '8 weeks' and (select data from d0)
            and data = (
                select max(data)
                from datas
                where date_trunc('day', data) = date_trunc('day', d.data)
            )
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
    execute format('
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
    ', par.b1, par.b0);
end loop;
end;
$body$;

    select data_serial as batch, data
    from datas
    where
        have_data
        and
        data <= '2012-06-09 18:20:00+00'::timestamptz - interval '50 days'
    order by data desc
    limit 1
;

select count(*)
  from donors_production_temp as up
  where up.n_time = 0
and active
;

select count(*)
from (
    select
        usuarios_indice.n_time,
        d0.pontos > coalesce (d50.pontos, 0) as active
    from usuarios as d0
      left outer join usuarios as d50 on d0.usuario = d50.usuario and d50.data = 23732
      inner join usuarios_indice on d0.usuario = usuario_serial
    where
    d0.data = 24388
) s
where active and n_time = 0
;

select *
from datas
where
	have_data
	and
	data <= (select max(data) from datas) - interval '50 days'
order by data desc
limit 1
;
