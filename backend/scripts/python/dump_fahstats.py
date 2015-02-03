import datetime
import os
d = datetime.datetime.today()
if d.hour >= 1 and d.hour <= 3:
   os.system('pg_dump folding > /home/cpn/backup/pgsql/folding.dump 2>> /home/cpn/backup/pgsql/folding.dump.err')
