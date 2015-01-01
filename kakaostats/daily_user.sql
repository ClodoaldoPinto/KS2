with d_56 as (
    select d - isodow(d) + 6 as "day"
    from (
        select (max(data) - interval '56 days')::date
        from datas
        ) s(d)
    )
select
    points, wus,
    to_char(data, 'YYYY-MM-DD') as "day",
    isodow(data) as dow
from (
    select
        pontos - lead(pontos, 1, 0::real) over w as points,
        wus - lead(wus, 1, 0) over w as wus,
        d.data
    from usuarios u
    inner join datas d on d.data_serial = u.data
    where
        usuario = 1829036
        and
        d.have_data
        and
        d.data in (
            select sq.data
            from (
                select
                    date_trunc('day', data) as day,
                    max(data) as data
                from datas
                where
                    data > (select "day" from d_56)
                group by day
                ) sq
            )
    window w as (order by d.data desc)
) ss
where
    points is not null
    and
    data > (select "day" from d_56) + 1
order by yearweek(data) desc, isodow(data)
;

