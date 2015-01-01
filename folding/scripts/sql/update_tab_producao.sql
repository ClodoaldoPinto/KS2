begin
select kstime(), insert_times_producao_temp, kstime();
analyze times_producao_temp;
select kstime(), update_ranking_times_temp(), kstime();

select kstime(), insert_usuarios_producao_temp(), kstime();
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
