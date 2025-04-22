# file: routes.py
from app import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.user_management.models import User
from app.user_management.util import *
from app import app
from app.email.emaillib import *
from datetime import datetime
import pytz
from app.backend_functions.exercise_backend import *
from app.backend_functions.misc import *
'''
###########################################################
############## WISHLIST, MARK AS NECESSARY ################
###########################################################

update plan []
search plans []
update days []
"post" plans [] (make plans available for search)
highlight current workouts on dashboard []


###########################################################
############## WISHLIST, MARK AS NECESSARY ################
###########################################################
'''
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
        
#should probably have this confirm the user is registered before we enable them to log on to anything else
@app.route('/verify', methods=['POST', 'GET'])
def verify_user():
    if request.method == 'POST':
        if 'OTP_FORM' in request.form:
            user = request.form.get('username')
            otp_entered = request.form.get('OTP_FORM')
            otp_code = request.form.get('OTP_CODE')
            email = request.form.get('email')
            password = request.form.get('password')

            print(f"POST (OTP): user = {user}, otp_entered = {otp_entered}, otp_code = {otp_code}, email={email}, password={password}")

            if otp_entered == otp_code:
                print("POST (OTP): user verified\n")
                return redirect(url_for('dashboard', username=user))
            else:
                print("POST (OTP): Invalid OTP")
                return render_template('verify.html', username=user, error_message="Invalid OTP. Please try again.", OTP_CODE=otp_code, email=email, password=password)  
        else:
            user = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            print("POST (Reg): USER INFO =", user, email, password)

            if user and email and password:
                valid = verify_new_user(user, email)
                otp = generate_OTP()
                send_auth_email(email, user, otp) 
                return render_template('verify.html', username=user, email=email, password=password, OTP_CODE=otp)
            else:
                print("POST (Reg): RETURNING REGISTER, NONUNIQUE CREDENTIALS")
                return render_template('register.html', error_message="Username or email already exists")
    elif request.method == 'GET':
        return render_template('register.html')

@app.route('/<username>/exercise_list', methods=['GET', 'POST'])
@login_required
def exercise_list(username):
    if current_user.username != username:
        return redirect(url_for('login'))
    muscle_groups = list_muscles()
    exercises = []
    default_equipment = list_equipment()
    ex_level = None
    name = None

    if request.method == 'POST':
        ex_level = request.form.get('ex_level')
        muscle_groups = request.form.getlist('muscle_group')
        selected_equipment = request.form.getlist('equip_group')
        exercises = get_exercises(muscle_groups, selected_equipment, ex_level, name)
        session['muscle_groups'] = muscle_groups
        session['ex_level'] = ex_level
        session['selected_equipment'] = selected_equipment
        return render_template('exercise_list.html', user=current_user, exercises=exercises, equipment_list=default_equipment, muscle_groups=muscle_groups, ex_level=ex_level, name=name)

    return render_template('exercise_list.html', user=current_user, exercises=exercises, equipment_list=default_equipment, muscle_groups=muscle_groups, ex_level=ex_level, name=name)

@app.route('/add_exercises_to_workout', methods=['POST'])
@login_required
def add_exercises_to_workout():
    if request.method == 'POST':
        selected_exercise_ids = request.form.getlist('selected_exercises')
        print("Selected Exercise IDs:", selected_exercise_ids)

        selected_exercises_list = []
        if selected_exercise_ids:
            selected_exercises_list = [int(eid) for eid in selected_exercise_ids]
            selected_exercises_list = select_exercises_for_plan(selected_exercises_list)

        session['added_exercises'] = selected_exercises_list 
        # session['muscle_groups'] = request.form.getlist('muscle_group')
        # session['ex_level'] = request.form.get('ex_level')
        # session['selected_equipment'] = request.form.getlist('equip_group')
        print("IN ADD_EX ROUTE, SEL_EX = ", selected_exercises_list)
        return redirect(url_for('exercise_plan', username=current_user.username, added_exercises=selected_exercises_list))
    return redirect(url_for('exercise_list', username=current_user.username))

@app.route('/<username>/exercise_plan', methods=['GET', 'POST'])
@login_required
def exercise_plan(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    now_utc = datetime.now(pytz.utc)
    central_timezone = pytz.timezone('America/Chicago')
    now_local = now_utc.astimezone(central_timezone)
    
    added_exercises = session.get('added_exercises', []) # get the exercises from the session
    muscle_groups = session.get('muscle_groups', [])
    ex_level = session.get('ex_level', '')
    selected_equipment = session.get('selected_equipment', [])

    if request.method == 'POST':
        #  Handle form submission from exercise_plan.html (if any)
        #  For example, saving the plan to the database.
        print("Form submitted from exercise_plan.html")
        print(request.form)
        return render_template('exercise_plan.html', user=current_user, now=now_local, username=username, added_exercises=added_exercises)

    else:
        print("GET request for exercise plan")
        return render_template('exercise_plan.html', user=current_user, now=now_local, username=username, added_exercises=added_exercises)
    
@app.route('/add_to_plan', methods=['POST'])
@login_required
def add_to_plan():
    selected_exercises_names = request.form.getlist('selected_exercises') # changed to selected_exercises
    print(selected_exercises_names)
    # Get the exercise details from the database based on the names
    selected_exercises_list = []

    if selected_exercises_names:
        for exercise_name in selected_exercises_names:
            # Assuming you have a function to get exercise details by name
            exercise_details = get_exercise_details_by_name(exercise_name) # you will need to create this function
            if exercise_details:
                selected_exercises_list.append(exercise_details)

    session['added_exercises'] = selected_exercises_list
    return redirect(url_for('exercise_plan', username=current_user.username))
