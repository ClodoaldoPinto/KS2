import psycopg
db = psycopg.connect("host=localhost dbname=fahstats")
cursor = db.cursor()
cursor.execute("select select_donors_data(0);")
donors_d0 = [linha[0] for linha in cursor.fetchall()]
cursor.execute("select select_donors_data(100);")
raw_list = [linha[0] for linha in cursor.fetchall()]
donors_d1 = dict(zip(raw_list, [None for donors in raw_list]))
del(raw_list)
nm = [donor for donor in donors_d0 if donor not in donors_d1]
del(donors_d0)
del(donors_d1)
cursor.execute("select select_donor_already_in_donor_first_wu()");
raw_list = [linha[0] for linha in cursor.fetchall()]
donors_already_in = dict(zip(raw_list, [None for donors in raw_list]))
del(raw_list)
for donor in [donor for donor in nm if donor not in donors_already_in]:
  cursor.execute("select insert_donor_first_wu(" + str(donor) + ");")
cursor.close()
db.commit()
db.close()

