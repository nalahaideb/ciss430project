# file: __init__.py
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
#from app.user_management.models import User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'key'
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# login_manager = LoginManager()
# login_manager.init_app(app)

from app import routes
