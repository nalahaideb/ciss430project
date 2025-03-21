# file: __init__.py
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config['SECRET_KEY'] = 'key'
toolbar = DebugToolbarExtension(app)

from app import routes
