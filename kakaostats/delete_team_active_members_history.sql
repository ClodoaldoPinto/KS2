-- Function: delete_team_active_members_history()

-- DROP FUNCTION delete_team_active_members_history();

CREATE OR REPLACE FUNCTION delete_team_active_members_history()
  RETURNS void AS
$BODY$
delete from team_active_members_history
where serial_date in (
    select de.data_serial
    from (
        select distinct d.data_serial, d.data
        from datas d
        inner join team_active_members_history tam on
            d.data_serial = tam.serial_date
    ) de
    where
        de.data < (
            select max(data)
            from datas
            where date_trunc('day', data) = date_trunc('day', de.data)
        )
        or
        de.data < (
            select max(data)
            from datas
            where
                date_trunc('month', data) = date_trunc('month', de.data)
                and
                data < (select max(data) from datas where have_data) - interval '8 weeks'
        )
)
;
$BODY$
  LANGUAGE sql VOLATILE STRICT
  COST 100;
ALTER FUNCTION delete_team_active_members_history()
  OWNER TO kakaostats;
