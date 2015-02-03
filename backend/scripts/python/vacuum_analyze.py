import psycopg2 as db
import os, sys, subprocess as sub
sys.path.append("/folding/scripts/python")
from setup import connStr

connection = db.connect(connStr["backend"])
cursor = connection.cursor()

query = """
select extract(hour from current_timestamp)::integer,
   extract(dow from current_timestamp)::integer;
"""
cursor.execute(query)
l = cursor.fetchall()[0]
hour = l[0]
dow = l[1]
connection.close()

if hour in (1, 2):

   #sub.call(["pgdump", "-U kakaostats", "-C", "folding", "> /folding/bak/dump/folding.dump", "2>> /folding/scripts/dump.Err.log"])
   os.system('pg_dump -Fp -U kakaostats -C folding > /folding/bak/dump/folding.dump 2>> /folding/scripts/dump.Err.log')

   if dow == 1:
      #sub.call(["psql", "-e", "-U kakaostats", "-c vacuum", "folding", "2>> /folding/scripts/vacuum.Err.log"])
      os.system('psql -e -U kakaostats -c "vacuum" folding 2>> /folding/scripts/vacuum.Err.log')

elif hour in (4, 5, 6):

   os.system('psql -e -U postgres -c "analyze" folding')
