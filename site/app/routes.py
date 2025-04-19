# file: routes.py
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.user_management.models import User
from app.user_management.util import *
from app import app
from app.email import *
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
    request_status = None
    show_accept_reject = False
    request_sent = False
    frid = None

    if not is_own_profile:
        user.is_friend = is_friends(current_user.id, user.id)

        if not user.is_friend:
            request_status = get_friend_request_status(current_user.id, user.id)
            if request_status['incoming']:
                show_accept_reject = True
                frid = request_status['incoming']
            elif request_status['outgoing']:
                request_sent = True
                frid = request_status['outgoing']

    pending_requests = get_friend_requests(current_user.id, limit=6) if is_own_profile else []
    sent_requests = get_sent_friend_requests(current_user.id, limit=6) if is_own_profile else []

    return render_template(
        'profile.html',
        user=user,
        show_add_friend=show_add_friend,
        show_accept_reject=show_accept_reject,
        request_sent=request_sent,
        frid=frid,
        pending_requests=pending_requests,
        sent_requests=sent_requests
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

    # Handle form search: redirect to clean GET
    if request.method == 'POST':
        search = request.form.get('search', '')
        return redirect(url_for(
            'friends',
            username=username,
            search=search,
            page_friends=1,
            page_users=1
        ))

    # Pull query and page states
    search_query = request.args.get('search', '')
    page_friends = int(request.args.get('page_friends', 1))
    page_users = int(request.args.get('page_users', 1))

    LIMIT = 10
    offset_friends = (page_friends - 1) * LIMIT
    offset_users = (page_users - 1) * LIMIT

    # Friends list
    friends = get_friends(uid, limit=LIMIT + 1, offset=offset_friends)
    has_more_friends = len(friends) > LIMIT
    friends = friends[:LIMIT]

    # Right-side list: mutual friends or full user search
    if search_query:
        users = search_users(search_query, exclude_uid=uid, limit=LIMIT + 1, offset=offset_users)
        right_header = "Users"
    else:
        users = get_mutual_users(uid, limit=LIMIT + 1, offset=offset_users)
        right_header = "Suggested Users (Mutual Friends)"

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
        has_more_users=has_more_users,
        search_query=search_query,
        right_header=right_header
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

@app.route('/cancel_friend_request/<int:frid>', methods=['POST'])
@login_required
def cancel_friend_request_route(frid):
    success = cancel_friend_request_by_id(frid, current_user.id)
    if success:
        flash("Friend request cancelled.")
    else:
        flash("Failed to cancel friend request.")
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
    
    muscle_groups = []
    ex_level = []
    exercises = [] 
    if request.method == 'POST':
        muscle_groups = request.form.getlist('muscle_group')
        ex_level = request.form.get('ex_level')
        equipment = request.form.get('equipment')
        #ex_name = request.form.get('search_field')
        exercises = get_exercises_from_db(muscle_groups, ex_level)
    #if request.method == 'GET':2
    return render_template('exercise_list.html', user=current_user, exercises=exercises, muscle_groups=muscle_groups, ex_level=ex_level)
        
@app.route('/<username>/exercise_plan', methods=['GET', 'POST'])
@login_required
def view_function(username):
    if current_user.username != username:
        return redirect(url_for('login'))
    exercises = [
        {'id': 1, 'name': 'Exercise A', 'level': 'Beginner', 'muscle_group': 'Group X'}
    ]
    now_utc = datetime.now(pytz.utc)
    current_timezone = pytz.timezone('America/Chicago')
    now_local = now_utc.astimezone(current_timezone)
    return render_template('exercise_plan.html', username=username, exercises=exercises, now=now_local)

#should probably have this confirm the user is registered before we enable them to log on to anything else
@app.route('/verify', methods=['POST', 'GET'])
def verify_user():
    user = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    print("USER INFO =", user, email, password)
    # basic input validation
    if not user or not email or not password:
        return "Error: Please fill in all fields.", 400

    # check if the username or email already exists in the database
    # existing_user = User.query.filter_by(username=username).first()
    # existing_email = User.query.filter_by(email=email).first()
    existing_user = None  
    existing_email = None 

    # if existing_user:
    #     return "Error: Username already exists.", 409
    # if existing_email:
    #     return "Error: Email already exists.", 409

    #hashed_password = generate_password_hash(password)

    # At this point, the data is valid and the user doesn't exist.
    # You would typically save this user data to your database here.
    # new_user = User(username=username, email=email, password_hash=hashed_password)
    # db.session.add(new_user)
    # db.session.commit()
    valid = verify_new_user(user, email) #replace with bool check for email/user uniqueness, OTP and password conf
    if valid:
        return render_template('verify.html', username=user, email=email, password=password)
    else:
        return render_template('register.html')

        
