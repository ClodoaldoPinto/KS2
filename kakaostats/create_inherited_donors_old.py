import psycopg2.extensions
from psycopg2.extras import RealDictConnection

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % (
    "localhost4", "5432", "fahstats", "kakaostats", "aroeira")

connection = RealDictConnection(conn_string)
connection.set_client_encoding('latin1')
cursor = connection.cursor()

query = """\
    set session work_mem = 2097152
    ;
    begin transaction isolation level serializable
    ;
    create table donor_work_old (like donors_old including constraints including defaults)
    ;
    alter table donors_old rename to donors_old_back
;"""

cursor.execute(query)

query = """\
    select distinct data
    from donors_old_back
;"""

cursor.execute(query)
rs = cursor.fetchall()
print 'datas:', len(rs)

for i, line in enumerate(rs):

    data = line['data']
    print i, data
    
    query = """\
    create table usuarios_%(data)s 
    (like donor_work_old including constraints including defaults)
    ;
    alter table usuarios_%(data)s add constraint b%(data)s
    check (data = %(data)s)
    ;
    insert into usuarios_%(data)s (data, usuario, wus, pontos)
        select data, usuario, wus, pontos
        from donors_old_back
        where data = %(data)s
    ;
    alter table usuarios_%(data)s
        add constraint fk_usuarios_%(data)s foreign key (data) references datas (data_serial)
    ;
    create unique index ndx_usuarios_%(data)s on usuarios_%(data)s (usuario)
    ;
    alter table usuarios_%(data)s inherit donor_work_old
    ;
    """ % {'data': data}

    cursor.execute(query)

cursor.execute('commit;')
connection.commit()
connection.close()
