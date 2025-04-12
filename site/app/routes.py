# file: routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User
from app import app
#from site_functions import *
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard', username=current_user.username))
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

@app.route('/<username>/exercise_list', methods=['GET', 'POST'])
def exercise_list(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('login'))

    muscle_groups = None # Initialize muscle groups
    ex_level = None # Initialize exercise level
    exercises = None # Initialize exercises

    if username == 'test':
        user = mock_user

        if request.method == 'POST':
            muscle_groups = request.form.getlist('muscle_group')
            ex_level = request.form.get('ex_level')
            #exercises = get_exercises_from_db(muscle_groups, ex_level)
            print("PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT", muscle_groups)

        return render_template('exercise_list.html', user=user, exercises=exercises, muscle_groups=muscle_groups, ex_level=ex_level)

    if request.method == 'POST':
        muscle_groups = request.form.getlist('muscle_group')
        ex_level = request.form.get('ex_level')
        exercises = get_exercises_from_db(muscle_groups, ex_level)

    return render_template('exercise_list.html', exercises=exercises, muscle_groups=muscle_groups, ex_level=ex_level)

# @app.route('/<username>/exercise_list', methods=['GET', 'POST'])
# def exercise_list(username):
#     if 'user' not in session or session['user'] != username:
#         return redirect(url_for('login'))

#     if username == 'test':
#         user = mock_user
#         exercises = None #initialize exercises
#         if request.method == 'POST':
#             muscle_groups = request.form.getlist('muscle_group')
#             ex_level = request.form.get('ex_level')
#             # print("PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT", muscle_groups)

#             #exercises = get_exercises_from_db(muscle_groups, ex_level)  # Fetch from DB.
#         return render_template('exercise_list.html', user=user, exercises=exercises)

#     exercises = None #initialize exercises
#     if request.method == 'POST':
#         muscle_groups = request.form.getlist('muscle_group')
#         ex_level = request.form.get('ex_level')
#         exercises = get_exercises_from_db(muscle_groups, ex_level) #Fetch from DB.
#     return render_template('exercise_list.html', exercises=exercises)

