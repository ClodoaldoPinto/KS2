create or replace function db_feed() returns void as
$body$
declare
batch integer;
begin

insert into datas (data)
select
    date_trunc( 'hour', last_date + interval '30 minute')
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
