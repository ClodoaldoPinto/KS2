\pset tuples_only on
\pset format unaligned
\encoding SQL_ASCII
\timing on
set session work_mem = 2097152;
truncate table times_temp;
truncate table usuarios_temp;
truncate table last_date_temp;
vacuum full usuarios_temp;
vacuum full times_temp;
vacuum full last_date_temp;
begin;
\copy last_date_temp (last_date) from 'data_usuarios.txt'
\copy times_temp (n_time, time_nome, pontos, wus) from 'daily_team_summary_out.txt'
\copy usuarios_temp (usuario, pontos, wus, n_time) from 'daily_user_summary_out.txt'
select db_feed();
commit;
-- ----------------------------------------------------------------------------
select kstime();
truncate table teams_production_temp;
truncate table donors_production_temp;
vacuum full teams_production_temp;
vacuum full donors_production_temp;

select update_last_date_temp();
select insert_teams_production_temp();
select update_teams_rank_temp();

drop index if exists ndx_donor_production_temp;
drop index if exists ndx_n_time_donor_production_temp;

select update_donors_rank_temp();
select create_ndx_donors_production_temp();
analyze donors_production_temp;

select update_team_total_members_temp();
select update_team_active_members_temp_2();
select update_donor_first_wu();
select update_team_new_members_temp_2();
select insert_project_total_teams_production_temp();

drop index ndx_teams_production;
drop index ndx_active_teams_production;
truncate table teams_production;
vacuum full teams_production;
insert into teams_production
  select * from teams_production_temp order by active, n_time;
create index ndx_teams_production on teams_production using btree (n_time);
create index ndx_active_teams_production
  on teams_production using btree (active);
truncate table donors_production;
vacuum full donors_production;
insert into donors_production
  select * from donors_production_temp order by n_time, active;
select update_last_date();

select insert_team_active_members_history();
select insert_donor_milestones();
update processing_end set "datetime" = now();
select delete_old();
select delete_team_active_members_history();
select update_donor_yearly();
select kstime();
--select now();
--reindex table times;select now();update maintenance set in_now = true;reindex table usuarios;update maintenance set in_now = false;select now();
