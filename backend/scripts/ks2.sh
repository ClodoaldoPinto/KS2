#!/bin/bash
echo "----------------------------------------------------------------------"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

pid_file=$SCRIPT_DIR"/ks2.pid"
if [ -e $pid_file ]
then
   echo 'pid file exists'
   exit 1
fi
touch $pid_file

# download new data files
date
echo 'baixa.py'
$SCRIPT_DIR"/python/baixa.py"


# parse the data files
date
echo 'parsebz2.py'
$SCRIPT_DIR"/python/parsebz2.py"
if [ $? -ne 0 ]
then
   rm -f $pid_file
   exit 1
fi

# rename and copy the data files to the backup directory
date
cp -p $SCRIPT_DIR"../files/daily_team_summary.txt.bz2" $SCRIPT_DIR"../bak/"$(ls -l --time-style=+%y-%m-%d-%H:%M $SCRIPT_DIR"../files/daily_team_summary.txt.bz2" | grep -P -o "\d\d-\d\d-\d\d-\d\d:\d\d")_team.txt.bz2
cp -p $SCRIPT_DIR"../files/daily_user_summary.txt.bz2" $SCRIPT_DIR"../bak/"$(ls -l --time-style=+%y-%m-%d-%H:%M $SCRIPT_DIR"../files/daily_user_summary.txt.bz2" | grep -P -o "\d\d-\d\d-\d\d-\d\d:\d\d")_user.txt.bz2

# run the db feed script
echo 'ks2.sql'
cd $SCRIPT_DIR"/../files"
psql -e -a --file $SCRIPT_DIR"/sql/folding.sql" -U folding folding

# vacuum the db
date
python $SCRIPT_DIR"/python/vacuum_analyze.py" 2>> $SCRIPT_DIR"/vacuum.Err.log"
date
rm -f $pid_file
