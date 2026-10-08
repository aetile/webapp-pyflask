import os
import sys
import logging
from flask import Flask
from config import Config
from auth import login_manager
from models import UserJSONEncoder

# App
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['KEY']
app.json_encoder = UserJSONEncoder
login_manager.init_app(app)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Env
sys.path.insert(0, '/opt/webgpa')
os.environ['PYTHONPATH'] = '/opt/webgpa'
os.environ['ORACLE_HOME'] = str(app.config['ORACLE_HOME'])
os.environ['LD_LIBRARY_PATH'] = str(app.config['LD_LIBRARY_PATH'])
os.environ['TNS_ADMIN'] = str(app.config['TNS_ADMIN'])
os.environ['AUTH_CLIENT_ID'] = str(app.config['AUTH_CLIENT_ID'])
os.environ['AUTH_CLIENT_SECRET'] = str(app.config['AUTH_CLIENT_SECRET'])
os.environ['AUTH_URL'] = str(app.config['AUTH_URL'])
os.environ['TOKEN_URL'] = str(app.config['TOKEN_URL'])
os.environ['USER_URL'] = str(app.config['USER_URL'])
os.environ['AUTH_CALLBACK_URL'] = str(app.config['AUTH_CALLBACK_URL'])
os.environ['PROXY'] = str(app.config['PROXY'])

# logging
logging.basicConfig(filename='/var/log/httpd/webgpa.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app():
  from routes import addz
  app.register_blueprint(addz)
  return app

if __name__ == '__main__':
  app = create_app()
  #app.run(host='0.0.0.0', port=5000, debug=True)
