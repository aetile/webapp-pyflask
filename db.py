import os
import oracledb
import sqlparse
import logging
import time
from flask import flash

logging.basicConfig(filename='/var/log/httpd/webgpa.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def init_db_conn():
  lib = os.environ['LD_LIBRARY_PATH']
  tns = os.environ['TNS_ADMIN']
  user = os.environ['DB_USER']
  password = os.environ['DB_PASSWORD']
  host = os.environ['DB_HOST']
  service = os.environ['DB_SERVICE']
  port = os.environ['DB_PORT']

  try:
    oracledb.init_oracle_client(lib_dir=lib, config_dir=tns)
    conn = oracledb.connect(user=user, password=password, host=host, port=port, service_name=service)
    return conn
  except oracledb.Error as err:
    obj_err, = err.args
    flash(obj_err.message, str(obj_err.code))
    logging.info(f"{obj_err.code}: {obj_err.message}")
    raise

def execute_query(query):
  result = None
  column_names = None
  start_time = time.time()
  logging.info(f"Query: {query}")
  try:
    if query:
      # Parsage de la requete SQL
      msg = parse_query(query)
      if msg:
        return None, None, msg

      # Execution securisee
      conn = init_db_conn()
      if conn and conn is not None:
        with conn.cursor() as cursor:
          cursor.execute(query)
          result = cursor.fetchall()
          end_time = time.time()
          execution_time = end_time - start_time
          logging.info(f"Query: {query}, Execution Time: {execution_time} seconds")
          column_names = [i[0] for i in cursor.description]
          return column_names, result, None
      else:
        return None, None, "Echec du pilote Oracle"
    else:
      return None, None, "Requête vide"
  except oracledb.Error as err:
    obj_err, = err.args
    return None, None, f"{obj_err.code}: {obj_err.message}"
  except Exception as err:
    logging.error(f"{str(err)}")
    return None, None, str(err)
  finally:
    if conn:
      conn.close()

def execute_file_query(file):
  column_names = ''
  results = ''
  error = ''
  try:
    with open(file, 'r', encoding='utf-8') as file:
      query = file.read()
      if query:
        column_names, results, error = execute_query(query)
        if error:
          flash(error, 'error')
          logging.info(f"Erreur: {str(error)}")
          return None, None, error
        else:
          return column_names, results, None
      else:
        return None, None, "Requête vide"
  except Exception as err:
    logging.error(f"{str(err)}")
    return None, None, f"Erreur de lecture du fichier: {file}"

def parse_query(query):
  result = ''
  if query:
    parsed = sqlparse.parse(query)
    first_token = parsed[0].tokens[0].value.lower()
    if first_token and first_token != 'select':
      result = "La requete doit etre un SELECT"

  return result
