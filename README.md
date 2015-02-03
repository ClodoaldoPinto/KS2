KS2
===

Completely rewritten version of KakaoStats

To install the db and users run the install.sh script

Add these lines to pg_hba.conf as the postgres user. Do not edit it as root

local    folding         folding                                 md5
host     folding         folding_web    127.0.0.1/32             md5

# To dump the schema only for repository purposes
pg_dump --schema-only -Ccsv --if-exists -d folding -U folding > ks2.schema

To feed the db run the backend/scripts/ks2.sh script for each new pair of data files.
It will create and remove the ks2.pid file.
If it gets stuck the pid file must be manually removed otherwise it will not run.
A crontab can be used to set it to run at the desired frequency.
