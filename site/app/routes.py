# file: routes.py
from flask import render_template, request, redirect, url_for, flash
from app import app

# NOTES
# flash messages are possible, but not sure if i want to use them
# commented out as of now as well as removed html support in base.html
#
# logic for login and register are placeholders to get the pages to work

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username.lower() == 'test' and password == 'pass':
            return redirect(url_for('dashboard'))
        else:
            #flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        terms = request.form.get('terms')
        if not terms:
            #flash('You must agree to the terms', 'warning')
            return redirect(url_for('register'))
        else:
            #flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
