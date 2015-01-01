-- Function: update_donors_rank_temp()

-- DROP FUNCTION update_donors_rank_temp();

CREATE OR REPLACE FUNCTION update_donors_rank_temp_text()
  RETURNS text AS
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
return format('
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
  LANGUAGE plpgsql stable
  COST 100;
ALTER FUNCTION update_donors_rank_temp_text()
  OWNER TO kakaostats;
