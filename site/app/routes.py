# file: routes.py
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    app.logger.info("entering index() ...")
    x = 42
    app.logger.info("x:", x)
    app.logger.info("exiting index() ...")
    return render_template('index.html', user='John')
