#!/usr/bin/env python

import psycopg2 as dbd, setup
from urllib import urlopen

query = """
select n_time
from teams_production
where n_time not in (-1)
order by active_members desc
limit 50
;"""

def main():

    connection = dbd.connect(setup.connStr["backend"])
    cursor = connection.cursor()
    cursor.execute(query)
    linhas = cursor.fetchall()
    cursor.close()
    connection.close()
    
    for linha in linhas:
      team_number = linha[0]
      print team_number
      urlopen('http://kakaostats.com/tsum.php?t=%s' % team_number).read()

main()
