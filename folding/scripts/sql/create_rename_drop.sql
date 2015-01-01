begin;

-- create table times_producao_temp
create table times_producao_temp
(
  n_time int4 not null,
  pontos_7 float4 not null,
  pontos_24 float4 not null,
  pontos_0 float4 not null,
  wus_0 int4 not null,
  wus_7 int4 not null,
  wus_24 int4 not null,
  rank_24 int4,
  rank_7 int4,
  rank_30 int4,
  pontos_14 float4 not null,
  rank_0 int4,
  active_members int4
) 
without oids;
alter table times_producao_temp owner to cpn;
grant all on table times_producao_temp to cpn;
grant select on table times_producao_temp to "phpuser";
create table times_producao_temp
(
  n_time int4 not null,
  pontos_7 float4 not null,
  pontos_24 float4 not null,
  pontos_0 float4 not null,
  wus_0 int4 not null,
  wus_7 int4 not null,
  wus_24 int4 not null,
  rank_24 int4,
  rank_7 int4,
  rank_30 int4,
  pontos_14 float4 not null,
  rank_0 int4,
  active_members int4
) 
without oids;
alter table times_producao_temp owner to cpn;
grant all on table times_producao_temp to cpn;
grant select on table times_producao_temp to "phpuser";

-- ---------------------------------------------------------------------------
-- insert times_producao_temp

select kstime(), insert_times_producao_temp(), kstime();
insert into times_producao_temp (
  n_time,
  pontos_0,
  pontos_24,
  pontos_7,
  pontos_14,
  wus_0,
  wus_24,
  wus_7
  )
  select n_time,
    sum (case when times.data = (select data_serial from datas order by data desc limit 1) then pontos else 0 end) as pontos_0,
    sum (case when times.data =
      (select data_serial from datas where data >=
        (select last_date from last_date) - (interval '1 day') order by data asc limit 1
      ) then pontos else 0 end) as pontos_24,
    sum (case when times.data =
      (select data_serial from datas where data >=
        (select last_date from last_date) - (interval '7 day') order by data asc limit 1
      ) then pontos else 0 end) as pontos_7,
    sum (case when times.data =
      (select data_serial from datas where data >=
        (select last_date from last_date) - (interval '14 day') order by data asc limit 1
      ) then pontos else 0 end) as pontos_14,
    sum (case when times.data = (select data_serial from datas order by data desc limit 1) then wus else 0 end ) as wus_0,
    sum (case when times.data =
     (select data_serial from datas where data >=
       (select last_date from last_date) - (interval '1 day') order by data asc limit 1
     ) then wus else 0 end) as wus_24,
    sum(case when times.data =
     (select data_serial from datas where data >=
       (select last_date from last_date) - (interval '7 day') order by data asc limit 1
     ) then wus else 0 end) as wus_7
   from times
   where
     times.data =
       (select data_serial from datas where data >=
         (select last_date from last_date) - (interval '1 day') order by data asc limit 1
       ) or
     times.data =
       (select data_serial from datas where data >=
       (select last_date from last_date) - (interval '7 day') order by data asc limit 1
       ) or
     times.data =
       (select data_serial from datas where data >=
         (select last_date from last_date) - (interval '14 day') order by data asc limit 1
       ) or
     times.data = ( select data_serial from datas order by data desc limit 1 )
    group by n_time
    --order by n_time
    ;

-- ------------------------------------------------------------------
--create ndx_times_producao_temp

select kstime(), create_ndx_times_producao_temp(), kstime();

CREATE INDEX "time_temp"
  ON times_producao_temp
  USING btree
  (n_time);
-- --------------------------------------------------------------------

analyze times_producao_temp;

-- --------------------------------------------------------------------
select kstime(), update_ranking_times_temp(), kstime();



select kstime(), create_tab_usuarios_producao_temp(), kstime();
select kstime(), insert_usuarios_producao_temp(), kstime();
select kstime(), create_ndx_tab_usuarios_producao_temp(), kstime();
analyze usuarios_producao_temp;
select kstime(), update_ranking_usuarios_temp(), kstime();
select kstime(), update_ranking_usuarios_time_temp(), kstime();

select kstime(), update_team_active_members_temp(), kstime();

drop table times_producao;
alter table times_producao_temp rename to times_producao;
alter index time_temp rename to time;

drop table usuarios_producao;
alter table usuarios_producao_temp rename to usuarios_producao;
alter index usuario_temp rename to usuario;
alter index usuarios_producao_n_time_temp rename to usuarios_producao_n_time;

select update_last_date();
commit;
analyze;
select kstime(), deleta_antigos3(), kstime();
