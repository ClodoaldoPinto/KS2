import config, psycopg2.extensions
from psycopg2.extras import RealDictConnection

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

def get_rs(queries):

   rs = dict()
   connection = RealDictConnection(config.conn_string)
   connection.set_client_encoding('latin1')
   cursor = connection.cursor()
   cursor.execute('begin transaction isolation level serializable;')
   for query_nome, query in queries.items():
      cursor.execute(query['query'], query.get('args', {}))
      rs[query_nome] = cursor.fetchall()
   cursor.execute('commit;')
   cursor.close()
   connection.close()

   return rs

def commit(query, d):

   connection = dbd.connect(config.conn_string)
   cursor = connection.cursor()
   try:
      cursor.execute(query, d)
      connection.commit()
   except:
      connection.close()
      raise

   cursor.close()
   connection.close()

def mogrify(query):

    connection = psycopg2.connect(config.conn_string)
    cursor = connection.cursor()
    query = cursor.mogrify(query['query'], query.get('args', {}))
    connection.close()

    return query
