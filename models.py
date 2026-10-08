import logging
import json
from flask_login import UserMixin, current_user

logging.basicConfig(filename='/var/log/httpd/webgpa.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class User(UserMixin):
  def __init__(self, user_id, email):
    self.id = user_id
    self.email = email

  def __repr__(self):
    return "User %s/%s" % (self.id, self.email)

  def is_active(self):
    return True

  def is_authenticated(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return self.id

class UserJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, User):
      return {'id': obj.id, 'email': obj.email}
