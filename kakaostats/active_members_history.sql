select data_serial, data
from datas_last_batch_of_each_day() d
where
	d.data < (select max(date_trunc('day', data)) from datas where have_data)
	and
	data_serial not in (
		select distinct serial_date
		from team_active_members_history
		where team_number = 0
		)
order by data desc
;

select max(data) as data, data_serial
from team_active_members_history t
inner join datas d on d.data_serial = t.serial_date
where team_number = 0
group by data_serial
order by data desc
limit 10

delete from team_active_members_history where serial_date = 22944;

select max(data) as data, data_serial
from datas
group by data_serial
order by data desc
