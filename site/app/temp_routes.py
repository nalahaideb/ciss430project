# file: routes.py
from flask import render_template, request, redirect, url_for, session
import pymysql

#from app.site_helper_functions import *

from app import app

#including these imports just for tests, having issues importing the helper functions
def get_exercises():
    #run filter_exercises and generate_filters before this once implemented
    conn = pymysql.connect(user='root', passwd='root')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute("use exdb;")

    target_muscles = request.form.getlist('muscle_group')
    print("TEST TEST TEST TEST TEST TEST TEST TEST ", target_muscles)
    c.execute("select ename, ebpart, erating from exercise;")
    
    #selected_categories = request.form.getlist('categories')

    if target_muscles:
        placeholders = ', '.join(['%s'] * len(selected_categories))
        query = f"select ename, ebpart, eequip from exercise where category IN ({placeholders})"
        print("QUERY TEST QUERY TEST QUERY TEST QUERY TEST QUERY TEST ", placeholders)
        c.execute(query, selected_categories)
        results = cursor.fetchall()
    else:
        results = []
    c.close()
    conn.close()
    return render_template('exdb_query_result.html', target_muscles=target_muscles, results=results)

# NOTES
# flash messages are possible, but not sure if i want to use them
# commented out as of now as well as removed html support in base.html
#
# logic for login and register are placeholders to get the pages to work
# temp user for placeholder
mock_user = {
    'username': 'test',
    'email': 'test@example.com',
    'bio': 'Just testing profile system',
    'goal': 'Build strength and stay fit'
}

@app.route('/')
@app.route('/index')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username.lower() == 'test' and password == 'pass':
            session['user'] = username
            return redirect(url_for('dashboard', username=username))
    return render_template('login.html')

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# NOTES
# Individualized dashboard for each user
@app.route('/<username>/dashboard')
def dashboard(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username == 'test':
        user = mock_user
        return render_template('dashboard.html', user=user)
    
    return "User not found", 404

# NOTES
# allow for multiple user profiles e.x. /profile/<username>
# allow edit_profile to access and update user table in database
@app.route('/<username>/profile')
def profile(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username == 'test':
        user = mock_user
        return render_template('profile.html', user=user)
    return "User not found", 404

@app.route('/<username>/edit_profile', methods=['GET', 'POST'])
def edit_profile(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username == 'test':
        user = mock_user
        if request.method == 'POST':
            # In real setup: update DB, validate form, etc.
            return redirect(url_for('profile', username=username))
        return render_template('edit_profile.html', user=user)
    return "User not found", 404

@app.route('/<username>/exercise_plan')
def exercise_plan(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username == 'test':
        user = mock_user
        return render_template('exercise_plan.html', user=user)
    return "User not found", 404

@app.route('/<username>/exercise_list')
def exercise_list(username, target_muscles = []):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    if username == 'test':
        user = mock_user
        get_exercises()
        return render_template('exercise_list.html', user=user)
    return "User not found", 404
