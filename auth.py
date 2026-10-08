from urllib.parse import urlencode
from flask import session
from flask_login import LoginManager
import requests
import logging
import models

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'addz.login'

# logging
logging.basicConfig(filename='/var/log/httpd/webgpa.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@login_manager.user_loader
def load_user(user_id):
  if 'user' in session and session['user'] and 'id' in session['user']:
    for uid, user in session['user'].items():
      if uid and uid == user_id:
        return user
      else:
        return models.User(-1, '')
  else:
    return models.User(-1, '')
  return None

def get_auth(code, client_id, client_secret, redirect_uri, token_url, user_url, proxy):
  user = None
  # Get auth code
  data = {'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': redirect_uri, 'code': code, 'grant_type': 'authorization_code', 'scope': 'openid email communities'}  # fin de ligne coupee sur la photo
  try:
    # Get token
    token = requests.post(token_url, data=data, proxies=proxy)
    token.raise_for_status()
    logging.info(f"Token: {token}")
    if token.status_code == 200:
      token_data = token.json()
      access_token = token_data['access_token']
      # Get user info
      headers = {'Authorization': 'Bearer ' + access_token}
      userinfo = requests.post(user_url, headers=headers, proxies=proxy)
      if userinfo.status_code == 200:
        user = userinfo.json()
        logging.info(f'User info: {user}')
  except requests.exceptions.RequestException as e:
    logging.error('Request failed: ' + str(e))

  return user
