-- Function: delete_old()

DROP FUNCTION delete_old_2();

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

if extract(hour from current_timestamp)::integer not between 1 and 24 then
    return;
end if;

d0 := (select max(data) from datas);
d15 := d0 - interval '15 days 1 hour';
d8w := d0 - interval '8 weeks 1 hour';
d1a := d0 - interval '1 year 1 hour';

create temporary table batch as
    select data_serial as batch
    from datas
    where data_serial not in (
        select data_serial
        from datas d
        where
            data = (
                select max(data)
                from datas
                where date_trunc('month', data) = date_trunc('month', d.data)
            )
            and
            data between d1a and d8w
        union
        select data_serial
        from datas d
        where
            data = (
                select max(data)
                from datas
                where date_trunc('day', data) = date_trunc('day', d.data)
            )
            and
            data between d8w and d15
        )
        and
        data < 	(select max(data) from datas) - interval '15 days'
        and have_data
;
-- teams ------------------------------------------
for rday in
    select distinct date_trunc('month', data) as "month"
    from datas
    where data between d1a and d8w
loop
    delete from times
    where data in (
        select data_serial as data_serial
        from datas
        where have_data
        and date_trunc('month', data) = rday.month
        and data < (
            select data
            from datas
            where date_trunc('month', data) = rday.month
            order by data desc
            limit 1
            )
        and data < d8w
    );
end loop;

for rday in
    select distinct date_trunc('day', data) as "day"
    from datas
    where data between d8w and d15
loop
    delete from times
    where data in (
        select data_serial as data_serial
        from datas
        where have_data
        and date_trunc('day', data) = rday.day
        and data < (
            select data
            from datas
            where date_trunc('day', data) = rday.day
            order by data desc
            limit 1
            )
    );
end loop;

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

return;
end;$BODY$
  LANGUAGE plpgsql VOLATILE STRICT
  COST 100;
ALTER FUNCTION delete_old()
  OWNER TO kakaostats;
