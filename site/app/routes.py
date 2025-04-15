# file: routes.py
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.user_management.models import User
from app.user_management.util import update_user_profile, update_last_login, get_friends, get_mutual_users, search_users, get_friend_requests, send_friend_request, approve_friend_request, reject_friend_request, remove_friend, is_friends
from app import app
from datetime import datetime
import pytz

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
    session.pop('_flashes', None)
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
        return "User not found", 404

    is_own_profile = current_user.username == username
    show_add_friend = not is_own_profile

    # Check if they're already friends
    user.is_friend = is_friends(current_user.id, user.id) if show_add_friend else False

    pending_requests = []
    if is_own_profile:
        pending_requests = get_friend_requests(current_user.id, limit=6)

    return render_template(
        'profile.html',
        user=user,
        show_add_friend=show_add_friend,
        pending_requests=pending_requests
    )

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

@app.route('/<username>/friends', methods=['GET', 'POST'])
@login_required
def friends(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    uid = current_user.id
    search_query = request.form.get('search') if request.method == 'POST' else request.args.get('search', '')

    LIMIT = 10
    page_friends = int(request.args.get('page_friends', 1))
    page_users = int(request.args.get('page_users', 1))

    offset_friends = (page_friends - 1) * LIMIT
    offset_users = (page_users - 1) * LIMIT

    # Friends list
    friends = get_friends(uid, limit=LIMIT + 1, offset=offset_friends)
    has_more_friends = len(friends) > LIMIT
    friends = friends[:LIMIT]

    # Users list
    if search_query:
        users = search_users(search_query, exclude_uid=uid, limit=LIMIT + 1, offset=offset_users)
    else:
        users = get_mutual_users(uid, limit=LIMIT + 1, offset=offset_users)

    has_more_users = len(users) > LIMIT
    users = users[:LIMIT]

    return render_template(
        'friends.html',
        user=current_user,
        friends=friends,
        users=users,
        page_friends=page_friends,
        page_users=page_users,
        has_more_friends=has_more_friends,
        has_more_users=has_more_users
    )

@app.route('/add_friend/<int:uid>', methods=['POST'])
@login_required
def add_friend(uid):
    if uid == current_user.id:
        flash("You cannot add yourself.")
        return redirect(request.referrer or url_for('dashboard', username=current_user.username))

    result = send_friend_request(current_user.id, uid)
    if result == "already_friends":
        flash("You are already friends.")
    elif result == "already_requested":
        flash("Friend request already sent.")
    elif result == "success":
        flash("Friend request sent.")
    else:
        flash("Failed to send friend request.")

    return redirect(request.referrer or url_for('profile', username=current_user.username))

@app.route('/approve_friend/<int:frid>', methods=['POST'])
@login_required
def approve_friend(frid):
    result = approve_friend_request(frid, current_user.id)
    if result == "success":
        flash("Friend request approved.")
    elif result == "invalid_request":
        flash("Invalid or expired friend request.")
    else:
        flash("Failed to approve friend.")
    return redirect(request.referrer or url_for('profile', username=current_user.username))

@app.route('/reject_friend/<int:frid>', methods=['POST'])
@login_required
def reject_friend(frid):
    result = reject_friend_request(frid, current_user.id)
    if result == "success":
        flash("Friend request rejected.")
    else:
        flash("Failed to reject friend request.")
    return redirect(request.referrer or url_for('profile', username=current_user.username))

@app.route('/remove_friend/<int:uid>', methods=['POST'])
@login_required
def remove_friend_route(uid):
    success = remove_friend(current_user.id, uid)
    if success:
        flash("Friend removed.")
    else:
        flash("Failed to remove friend.")
    return redirect(request.referrer or url_for('profile', username=current_user.username))



@app.route('/<username>/exercise_plan')
@login_required
def exercise_plan(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    now_utc = datetime.now(pytz.utc)
    central_timezone = pytz.timezone('America/Chicago')
    now_local = now_utc.astimezone(central_timezone)

    #dummy data for now
    exercises = [
        {'id': 1, 'name': 'Push-ups', 'level': 'Beginner', 'muscle_group': 'Chest'},
        {'id': 2, 'name': 'Squats', 'level': 'Beginner', 'muscle_group': 'Legs'},
    ]

    return render_template('exercise_plan.html', user=current_user, now=now_local, username=username, exercises=exercises)

@app.route('/<username>/exercise_list', methods=['GET', 'POST'])
@login_required
def exercise_list(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    muscle_groups = None
    ex_level = None 
    exercises = None 

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


@app.route('/<username>/exercise_plan', methods=['GET', 'POST'])
@login_required
def view_function():
    username = "example_user" 
    exercises = [
        {'id': 1, 'name': 'Exercise A', 'level': 'Beginner', 'muscle_group': 'Group X'}
    ]
    now_utc = datetime.now(pytz.utc)
    current_timezone = pytz.timezone('America/Chicago')
    now_local = now_utc.astimezone(current_timezone)
    return render_template('exercise_plan.html', username=username, exercises=exercises, now=now_local)
