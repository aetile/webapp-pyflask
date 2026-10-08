import os
import uuid
from dotenv import load_dotenv

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))

class Config:
  KEY = os.environ.get('KEY')
  ORACLE_HOME = os.environ.get('ORACLE_HOME')
  LD_LIBRARY_PATH = os.environ.get('LD_LIBRARY_PATH')
  TNS_ADMIN = os.environ.get('TNS_ADMIN')
  PATH = os.environ.get('PATH')
  DB_USER = os.environ.get('DB_USER')
  DB_PASSWORD = os.environ.get('DB_PASSWORD')
  DB_HOST = os.environ.get('DB_HOST')
  DB_SERVICE = os.environ.get('DB_SERVICE')
  DB_PORT = os.environ.get('DB_PORT')
  AUTH_CLIENT_ID = os.environ.get('AUTH_CLIENT_ID')
  AUTH_CLIENT_SECRET = os.environ.get('AUTH_CLIENT_SECRET')
  AUTH_ISSUER = os.environ.get('AUTH_ISSUER')
  AUTH_URL = os.environ.get('AUTH_URL')
  TOKEN_URL = os.environ.get('TOKEN_URL')
  USER_URL = os.environ.get('USER_URL')
  AUTH_CALLBACK_URL = os.environ.get('AUTH_CALLBACK_URL')
  PROXY = os.environ.get('PROXY')
