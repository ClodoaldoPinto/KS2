#! /usr/bin/env python
import psycopg
def fetchsome(cursor, arraysize=10000):
  ''' A generator that simplifies the use of fetchmany '''
  while True:
    results = cursor.fetchmany(arraysize)
    if not results: break
    for result in results:
      yield result

db = psycopg.connect("host=localhost dbname=fahstats")

cursor_0 = db.cursor()
cursor_0.execute("select select_donors_data(0);")
donors_d0 = (linha[0] for linha in fetchsome(cursor_0))

cursor_1 = db.cursor()
cursor_1.execute("select select_donors_data(100);")
raw_list = (linha[0] for linha in fetchsome(cursor_1))

donors_d1 = dict.fromkeys(raw_list)
nm = (donor for donor in donors_d0 if donor not in donors_d1)

cursor_2 = db.cursor()
cursor_2.execute("select select_donor_already_in_donor_first_wu()");
raw_list = (linha[0] for linha in fetchsome(cursor_2))
donors_already_in = dict.fromkeys(raw_list)

cursor_3 = db.cursor()
for donor in (donor for donor in nm if donor not in donors_already_in):
  cursor_3.execute("select insert_donor_first_wu(" + str(donor) + ");")
db.commit()
db.close()

