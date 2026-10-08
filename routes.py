import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from auth import get_auth
from models import User
from urllib.parse import urlencode
from db import execute_query, execute_file_query
from datetime import datetime
import logging
import json

# App
addz = Blueprint('addz', __name__)

# logging
logging.basicConfig(filename='/var/log/httpd/webgpa.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def safe_redirect(url, max_retries=3):
  for attempt in range(max_retries):
    try:
      return redirect(url)
    except Exception as e:
      logging.error(f"Redirection attempt {attempt + 1} failed: {e}")
      if attempt == max_retries - 1:
        # Si c'est la dernière tentative, lever une exception ou gérer l'erreur
        return "Erreur de redirection, veuillez réessayer plus tard.", 500

# IHM Tabs
@addz.route('/')
def index():
  #return redirect(url_for('addz.login', next='select', _external=True))
  return redirect(url_for('addz.login', _external=True))

@addz.route('/login', methods=['GET','POST'])
def login():
  logging.info(f"Session: {session}")
  if 'tab' not in session:
    session['tab'] = 'select'
  auth_url = os.environ['AUTH_URL']
  client_id = os.environ['AUTH_CLIENT_ID']
  redirect_uri = os.environ['AUTH_CALLBACK_URL']
  url_params = dict(client_id=client_id, redirect_uri=redirect_uri, scope='openid email communities', response_type='code')
  url = auth_url + ('?' + urlencode(url_params) if url_params else '')
  logging.info(f"Tab: {session['tab']}")
  logging.info(f"HTTP request: {request}")
  logging.info(f"Redirect: {url}")
  # Process authentication
  if request.method == 'GET':
    if 'next' in request.args:
      tab = request.args.get('next')
      session['tab'] = tab.lstrip('/')
      logging.info('**************************')
      logging.info(f"Next Tab: {session['tab']}")
    if 'code' in request.args and current_user.is_anonymous:
      app_user = User(-1,'')
      auth_code = request.args.get('code')
      client_id = os.environ['AUTH_CLIENT_ID']
      client_secret = os.environ['AUTH_CLIENT_SECRET']
      redirect_uri = os.environ['AUTH_CALLBACK_URL']
      token_url = os.environ['TOKEN_URL']
      user_url = os.environ['USER_URL']
      proxy = {'https': 'http://' + os.environ['PROXY']}
      logging.info(f"Proxy: {proxy}")
      logging.info(f"{auth_code}, {client_id}, {client_secret}, {redirect_uri}, {token_url}, {user_url}, {proxy}")
      user = get_auth(auth_code, client_id, client_secret, redirect_uri, token_url, user_url, proxy)
      logging.info(f"User: {user}")
      if user:
        app_user = User(user_id=user['sub'], email=user['email'])
        session['user'] = app_user
        logging.info(f"Connecting user {user['sub']}")
        login_user(app_user, remember=True)
        return redirect(url_for('addz.' + session['tab'], _external=True))
    else:
      if 'user' in session:
        logging.info(f"Reconnecting user {user['sub']}")
        login_user(session['user'], remember=False)
        return redirect(url_for('addz.' + session['tab'], _external=True))
  if url:
    logging.info(f"Redirect: {url}")
    return redirect(url)

@addz.route('/select', methods=['GET', 'POST'])
@login_required
def select():
  session['tab'] = 'select'
  column_names = []
  results = []
  if 'select' not in session:
    session['select'] = {}
    session['select'].setdefault('query', '')
    session['select'].setdefault('columns', [])
    session['select'].setdefault('result', [])
  logging.info('**************************')
  logging.info(f"Tab: {session['tab']}")
  logging.info(f"{request}")
  logging.info(f"BEFORE Session")
  logging.info(f"Session: {session}")
  logging.info(f"AFTER Session")
  if request.method == 'POST':
    session['select']['query'] = request.form['sql_query']
    if session['select']['query']:
      logging.info(f"{session['select']['query']}")
      column_names, results, error = execute_query(session['select']['query'])
      #session['select']['columns'] = column_names
      #session['select']['result'] = results
      if error:
        flash(error, 'error')
        logging.info(f"{error}")

  logging.info(f"Result: {session['select']['result']}")
  return render_template('query.html', current_tab='select', tab_title='Select', select=session['select']['query'], select_columns=column_names, select_result=results)

@addz.route('/gpa', methods=['GET', 'POST'])
@login_required
def gpa():
  session['tab'] = 'gpa'
  if 'gpa' not in session:
    session['gpa'] = {}
    session.setdefault('gpa', {})
    session['gpa'].setdefault('contents', {})
  sql_dir = '/opt/webgpa/gpa'
  list_dir = os.listdir(sql_dir)
  content_gpa = {}
  logging.info('**************************')
  logging.info(f"Tab: {session['tab']}")
  logging.info(f"{request}")
  logging.info(f"BEFORE Session")
  logging.info(f"Session: {session}")
  logging.info(f"AFTER Session")

  if request.method == 'POST':
    # Execution de la fonction execute_file_query sur chaque fichier SQL
    for file in list_dir:
      result = []
      columns = []
      filename = os.path.splitext(file)[0]
      logging.info(f"processing file: {file}")
      if file and os.path.isfile(os.path.join(sql_dir, file)):
        try:
          columns, result, error = execute_file_query(os.path.join(sql_dir, file))
          # Ajout du resultat dans un dictionnaire
          if result:
            #logging.info(f"Result: {str(result)}")
            content_gpa[filename] = {
              'columns': columns,
              'result': result
            }
          else:
            logging.info("No Result")
            #flash('No Result')
        except Exception as e:
          logging.error(f"Error processing file {file}: {str(e)}")
          flash(f"Error processing file {file}", 'error')
      else:
        logging.info(f"File not found: {sql_dir}//{file}", 'error')
        flash(f"File not found: {sql_dir}/{file}", 'error')
    #session['gpa']['contents'] = content_gpa

  logging.info(f"Content: {content_gpa}")
  return render_template('query.html', current_tab='gpa', tab_title='GPA', content_gpa=content_gpa)

@addz.route('/suiviprod', methods=['GET', 'POST'])
@login_required
def suiviprod():
  session['tab'] = 'suiviprod'
  tables = []
  if 'suiviprod' not in session:
    session['suiviprod'] = {}
    session.setdefault('suiviprod', {})
    session['suiviprod'].setdefault('contents', {})
  sql_dir = '/opt/webgpa/sql'
  #list_dir = ['import.sql','LOTS_AVT_SIGNATURE_SDD_RECURRENT.sql']
  list_dir = os.listdir(sql_dir)
  content_suiviprod = {}
  logging.info('**************************')
  logging.info(f"Tab: {session['tab']}")
  logging.info(f"{request}")
  logging.info(f"BEFORE Session")
  logging.info(f"Session: {session}")
  logging.info(f"AFTER Session")
  logging.info(f"File list: {list_dir}")

  if request.method == 'POST':
    # Execution de la fonction execute_file_query sur chaque fichier SQL
    for file in list_dir:
      result = []
      columns = []
      filename = os.path.splitext(file)[0].lower()
      logging.info(f"processing file: {file}")
      if file and os.path.isfile(os.path.join(sql_dir, file)):
        try:
          columns, result, error = execute_file_query(os.path.join(sql_dir, file))
          # Ajout du résultat dans un dictionnaire
          if result:
            #logging.info(f"Result: {str(result)}")
            tables.append(f"{filename[0:30]}-table")
            content_suiviprod[filename] = {
              'columns': columns,
              'result': result
            }
          else:
            logging.info("No Result")
            #flash('No Result')
        except Exception as e:
          logging.error(f"Error processing file {file}: {str(e)}")
          flash(f"Error processing file {file}", 'error')
      else:
        logging.info(f"File not found: {sql_dir}//{file}", 'error')
        flash(f"File not found: {sql_dir}/{file}", 'error')
    #session['suiviprod']['contents'] = content_suiviprod

  logging.info(f"Content: {content_suiviprod}")
  logging.info(f"Tables list: {tables}")
  return render_template('query.html', current_tab='suiviprod', tab_title='SuiviProd', content_suiviprod=content_suiviprod, tables=json.dumps(tables))

@addz.route('/logout')
@login_required
def logout():
  logout_user()
  #session.clear()
  return redirect(url_for('addz.index', _external=True))

@addz.route('/img/<path:filename>')
def send_img(filename):
  return send_from_directory('img', filename)

@addz.route('/healthcheck', methods=['GET'])
def healthcheck():
  return 'OK', 200

@addz.route('/log_export', methods=['POST'])
def log_export():
  tab = session.get('tab')
  user = session.get('_user_id')
  query = session[tab].get('query', '')

  # Log l'exportation (ici, simplement imprimé dans la console)
  logging.info(f"User {user} exported tab {tab} to file. {query}")
  return jsonify({'status': 'success', 'message': 'Export logged successfully'}), 200
