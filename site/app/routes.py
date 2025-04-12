# file: routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.user_management.models import User
from app.user_management.util import update_user_profile, update_last_login
from app import app
#from site_functions import *


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

        user = User.get_by_username(username)
        if user and check_password_hash(user.phash, password):
            update_last_login(user.ucid)
            user = User.get_by_username(user.username)
            login_user(user)
            return redirect(url_for('dashboard', username=user.username))
        flash('Invalid username or password.')
        
    return render_template('login.html')

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/<username>/dashboard')
@login_required
def dashboard(username):
    if current_user.username != username:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=current_user)

@app.route('/<username>/profile')
@login_required
def profile(username):
    user = User.get_by_username(username)
    if not user:
        return "User not found, 404"
    return render_template('profile.html', user=user)

@app.route('/<username>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        bio = request.form.get('bio')

        success = update_user_profile(current_user.id, current_user.ucid, fname, lname, email, bio)
        if success:
            flash('Profile updated successfully.')
        else:
            flash('An error occurred while updating your profile.')
            
        return redirect(url_for('profile', username=username))
    
    return render_template('edit_profile.html', user=current_user)


@app.route('/<username>/exercise_plan')
@login_required
def exercise_plan(username):
    if current_user.username != username:
        return redirect(url_for('login'))
    return render_template('exercise_plan.html', user=current_user)

@app.route('/<username>/exercise_list', methods=['GET', 'POST'])
@login_required
def exercise_list(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    muscle_groups = None # Initialize muscle groups
    ex_level = None # Initialize exercise level
    exercises = None # Initialize exercises

    if request.method == 'POST':
        muscle_groups = request.form.getlist('muscle_group')
        ex_level = request.form.get('ex_level')
        #exercises = get_exercises_from_db(muscle_groups, ex_level)
        print("PRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINTPRINT", muscle_groups)

    return render_template('exercise_list.html', user=current_user, exercises=exercises, muscle_groups=muscle_groups, ex_level=ex_level)

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

