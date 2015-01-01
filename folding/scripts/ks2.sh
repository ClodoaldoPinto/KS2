#!/bin/bash
echo "----------------------------------------------------------------------"
pid_file=/folding/scripts/ks2.pid
if [ -e $pid_file ]
then
   echo 'pid file exists'
   exit 1
fi
touch $pid_file
date
cd /folding/arquivos/
echo 'baixa.py'
/folding/scripts/python/baixa.py
date
echo 'parsebz2.py'
/folding/scripts/python/parsebz2.py
if [ $? -ne 0 ]
then
   rm -f $pid_file
   exit 1
fi
date
cp -p /folding/arquivos/daily_team_summary.txt.bz2 /folding/bak/$(ls -l --time-style=+%y-%m-%d-%H:%M /folding/arquivos/daily_team_summary.txt.bz2 | grep -P -o "\d\d-\d\d-\d\d-\d\d:\d\d")_team.txt.bz2
cp -p /folding/arquivos/daily_user_summary.txt.bz2 /folding/bak/$(ls -l --time-style=+%y-%m-%d-%H:%M /folding/arquivos/daily_user_summary.txt.bz2 | grep -P -o "\d\d-\d\d-\d\d-\d\d:\d\d")_user.txt.bz2
echo 'ks2.sql'
psql -e --file /folding/scripts/sql/folding.sql -U kakaostats folding
#2>> /folding/scripts/folding.sql.Err.log
#date
#python /folding/scripts/python/team_summary_fetch.py 2>> /folding/scripts/team_summary_fetch.Err.log
date
python /folding/scripts/python/vacuum_analyze.py 2>> /folding/scripts/vacuum.Err.log
date
rm -f $pid_file
#python /folding/scripts/python/dump_fahstats.py
#date
#psql -e -c "vacuum analyze" folding
#date
#psql -e -c "cluster ndx_times_time_data on times" folding
#date
#psql -e -c "cluster times_indice_pkey on times_indice" folding
#date
#psql -e -c "cluster ndx_usuarios_data on usuarios" folding
#date
#psql -e -c "cluster usuarios_indice_pkey on usuarios_indice" folding
#date
#psql -e -c "cluster data_ndx on datas" folding
#date
