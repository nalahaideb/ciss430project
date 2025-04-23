# file: routes.py
from app import app
from flask import render_template, request, redirect, url_for, flash, session, jsonify
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

update plan [x]
search plans []
update days [x]
"post" plans [] (make plans available for search)
highlight current workouts on dashboard [x]
add exercises to db []
progress page []
progress graph on dashboard for current exercises []

potential:
password reset []
reordering of days []
reordering of exercises []

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
    
    plan = get_main_plan_with_days(current_user.id)
    
    return render_template('dashboard.html', 
                         user=current_user,
                         plan=plan)

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
    if request.method == 'POST':
        search = request.form.get('search', '')
        return redirect(url_for(
            'friends',
            username=username,
            search=search,
            page_friends=1,
            page_users=1
        ))
    search_query = request.args.get('search', '')
    page_friends = int(request.args.get('page_friends', 1))
    page_users = int(request.args.get('page_users', 1))

    LIMIT = 10
    offset_friends = (page_friends - 1) * LIMIT
    offset_users = (page_users - 1) * LIMIT
    friends = get_friends(uid, limit=LIMIT + 1, offset=offset_friends)
    has_more_friends = len(friends) > LIMIT
    friends = friends[:LIMIT]
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
        selected_exercises_list = []
        
        if selected_exercise_ids:
            exercise_ids = [int(eid) for eid in selected_exercise_ids]
            exercises = select_exercises_for_plan(exercise_ids)
            if exercises and isinstance(exercises[0], dict):
                session['added_exercises'] = exercises
            else:
                session['added_exercises'] = [{
                    'id': ex.id,
                    'ename': ex.ename,
                    'level': ex.level,
                    'muscle_group': ex.muscle_group
                } for ex in exercises]
            
        #print("Stored exercises:", session['added_exercises'])
        return redirect(url_for('exercise_plan', username=current_user.username))
    return redirect(url_for('exercise_list', username=current_user.username))

@app.route('/<username>/exercise_plan', methods=['GET', 'POST'])
@login_required
def exercise_plan(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    now_utc = datetime.now(pytz.utc)
    central_timezone = pytz.timezone('America/Chicago')
    now_local = now_utc.astimezone(central_timezone)
    
    added_exercises = session.get('added_exercises', [])

    user_plan_days = get_user_plan_days(current_user.id)
    
    return render_template('exercise_plan.html', 
                          user=current_user, 
                          now=now_local, 
                          username=username, 
                          added_exercises=added_exercises,
                          user_plan_days=user_plan_days)

@app.route('/add_day', methods=['POST'])
@login_required
def add_day():
    if request.method == 'POST':
        day_name = request.form.get('day_name')
        
        if not day_name:
            flash('Day name is required.')
            return redirect(url_for('exercise_plan', username=current_user.username))
        success = add_plan_day(current_user.id, day_name)
        
        if success:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Exercise_Plan 
                SET creation_date = NOW() 
                WHERE pid = (SELECT main_pid FROM User WHERE uid = %s)
            """, (current_user.id,))
            conn.commit()
            conn.close()
            
            flash(f'Day "{day_name}" added successfully.')
        else:
            flash('Failed to add day.')
            
        return redirect(url_for('exercise_plan', username=current_user.username))
    
@app.route('/add_to_plan', methods=['POST'])
@login_required
def add_to_plan():
    if request.method == 'POST':
        day_id = request.form.get('selected_day')
        selected_exercise_ids = request.form.getlist('selected_exercises')
        print("SELECTED_EXERCISES", selected_exercise_ids)
        selected_exercise_ids = [eid for eid in selected_exercise_ids if eid]
        
        print("Day ID:", day_id)
        if not day_id:
            flash('Please select a day to add exercises to.')
            return redirect(url_for('exercise_plan', username=current_user.username))
        
        if not selected_exercise_ids:
            flash('Please select at least one exercise to add.')
            return redirect(url_for('exercise_plan', username=current_user.username))
        added_count = add_exercises_to_day(day_id, selected_exercise_ids)
        
        if added_count > 0:
            flash(f'{added_count} exercise(s) added to your plan.')
        else:
            flash('No exercises were added to your plan.')
            
        return redirect(url_for('exercise_plan', username=current_user.username))
    
@app.route('/remove_exercise_from_day', methods=['POST'])
@login_required
def remove_exercise_from_day():
    if request.method == 'POST':
        data = request.get_json()
        day_id = data.get('day_id')
        exercise_id = data.get('exercise_id')
        
        if not day_id or not exercise_id:
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        day_owner = get_day_owner_id(day_id)
        if day_owner != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized access'})
        success = remove_exercise_from_plan_day(day_id, exercise_id)
        
        return jsonify({'success': success})

@app.route('/edit_day_name', methods=['POST'])
@login_required
def edit_day_name():
    if request.method == 'POST':
        data = request.get_json()
        day_id = data.get('day_id')
        new_name = data.get('new_name')
        
        if not day_id or not new_name:
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        day_owner = get_day_owner_id(day_id)
        if day_owner != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized access'})
        success = update_plan_day_name(day_id, new_name)
        
        return jsonify({'success': success})

@app.route('/remove_day', methods=['POST'])
@login_required
def remove_day():
    if request.method == 'POST':
        data = request.get_json()
        day_id = data.get('day_id')
        
        if not day_id:
            return jsonify({'success': False, 'message': 'Missing required parameter'})
        day_owner = get_day_owner_id(day_id)
        if day_owner != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized access'})
        success = delete_plan_day(day_id)
        
        return jsonify({'success': success})

@app.route('/create_plan', methods=['POST'])
@login_required
def create_plan():
    plan_id = create_default_plan(current_user.id)
    if plan_id:
        flash('New workout plan created successfully!')
    else:
        flash('Failed to create plan')
    return redirect(url_for('exercise_plan', username=current_user.username))

@app.route('/get_plan_days/<int:plan_id>')
@login_required
def get_plan_days(plan_id):
    """Get days for selected plan"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT did, day_name FROM Exercise_Plan_Day 
                WHERE pid = %s ORDER BY day_order
            """, (plan_id,))
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/get_day_exercises/<int:day_id>')
@login_required
def get_day_exercises(day_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT epe.entry_id, e.ename 
                FROM Exercise_Entry epe
                JOIN Exercises e ON epe.eid = e.eid
                WHERE epe.did = %s
                ORDER BY epe.exercise_order
            """, (day_id,))
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/get_exercise_details/<int:entry_id>')
@login_required
def get_exercise_details(entry_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT sets, reps FROM Exercise_Entry 
                WHERE entry_id = %s
            """, (entry_id,))
            return jsonify(cursor.fetchone())
    finally:
        conn.close()

@app.route('/get_progress_history/<int:entry_id>')
@login_required
def get_progress_history(entry_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT sets_completed, reps_completed, weight_used, notes, recorded_at
                FROM Exercise_Progress
                WHERE entry_id = %s
                ORDER BY recorded_at DESC
            """, (entry_id,))
            return jsonify(cursor.fetchall())
    finally:
        conn.close()

@app.route('/save_progress/<int:entry_id>', methods=['POST'])
@login_required
def save_progress(entry_id):
    data = request.json
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Exercise_Progress 
                (entry_id, sets_completed, reps_completed, weight_used, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (entry_id, data['sets_completed'], data['reps_completed'], 
                 data.get('weight_used'), data.get('notes')))
            conn.commit()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

@app.route('/<username>/progress')
@login_required
def progress(username):
    if current_user.username != username:
        return redirect(url_for('login'))
    plan = get_main_plan_with_days(current_user.id)
    
    return render_template('progress.html', 
                         user=current_user,
                         plan=plan)
