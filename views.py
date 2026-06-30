from flask import Blueprint,render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Booking, Bootcamp


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')
#Admin Functionalities

@login_required
@views.route('/admin')
def admin_dashboard():
    if current_user.role != 'admin':
        return "unauthorized", 403
    #search
    search_query = request.args.get('search', '')

    if search_query:
        search_term = f"%{search_query}%"
        bootcamps = Bootcamp.query.filter(Bootcamp.title.ilike(search_term)).all()
        mentors = User.query.filter(User.role == 'mentor', User.username.ilike(search_term)).all()
        students = User.query.filter(User.role == 'student', User.username.ilike(search_term)).all()
    else:
        bootcamps = Bootcamp.query.all()
        mentors = User.query.filter_by(role = 'mentor').all()
        students = User.query.filter_by(role = 'student').all()

    #data for chart(Bookings per bootcamp)
    all_bootcamps_for_chart = Bootcamp.query.all()
    chart_labels = [b.title for b in all_bootcamps_for_chart]
    chart_data = [len(b.bookings) for b in all_bootcamps_for_chart]

    return render_template('admin_dashboard.html', bootcamps = bootcamps, mentors = mentors, students = students, search_query = search_query, chart_labels = chart_labels, chart_data = chart_data)


@login_required
@views.route('/create_bootcamp', methods = ['POST'])
def create_bootcamp():
        if current_user.role != 'admin':
            return "unauthorized", 403
        
        title = request.form.get('title')
        slots = request.form.get('slots_available')
        new_bootcamp = Bootcamp(title = title, slots_available = slots)
        db.session.add(new_bootcamp)
        db.session.commit()

        flash('Bootcamp created succssfully', 'success')
        return redirect(url_for('views.admin_dashboard'))



@login_required
@views.route('/delete_bootcamp/<int:id>')
def delete_bootcamp(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    bootcamp = Bootcamp.query.get_or_404(id)
    db.session.delete(bootcamp)
    db.session.commit()
    flash("Bootcamp deleted successfully", 'info')
    return redirect(url_for('views.admin_dashboard'))

@login_required
@views.route('/assign_mentor/<int:bootcamp_id>', methods = ['POST'])
def assign_mentor(bootcamp_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    bootcamp = Bootcamp.query.get_or_404(bootcamp_id)
    mentor_id = request.form.get('mentor_id')
    bootcamp.mentor_id = mentor_id
    db.session.commit()
    flash("Mentor Assigned", 'success')
    return redirect(url_for('views.admin_dashboard'))

@login_required
@views.route('/toggle_user_status/<int:user_id>/<action>')
def toggle_user_status(user_id, action):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    user = User.query.get_or_404(user_id)

    if action == 'approve':
        user.is_approved = True
        flash(f'Mentor {user.username} approved', 'success')
    elif action == 'blacklist':
        user.is_blacklisted = not user.is_blacklisted
        status = "blacklisted" if user.is_blacklisted else "restored"
        flash(f'User {user.username} {status}.', 'warning')
    db.session.commit()
    return redirect(url_for('views.admin_dashboard'))

#Mentor routes

@login_required
@views.route('/mentor_dashboard')
def mentor_dashboard():
    if current_user.role != 'mentor' : return "Unauthorized", 403
    assigned_bootcamps = Bootcamp.query.filter_by(mentor_id = current_user.id).all()
    return render_template('mentor_dashboard.html', bootcamps = assigned_bootcamps)

@login_required
@views.route('/update_status/<int:bootcamp_id>', methods = ['POST'])
def update_status(bootcamp_id):
    if current_user.role != 'mentor' : return "Unauthorized", 403
    bootcamp = Bootcamp.query.get_or_404(bootcamp_id)

    if bootcamp.mentor_id == current_user.id:
        bootcamp.status = request.form.get('status')
        db.session.commit()
        flash('Status updated', 'success')
    return redirect(url_for('views.mentor_dashboard'))

#Student routes

@login_required
@views.route('/student_dashboard')
def student_dashboard():
    if current_user.role != 'student': return "Unauthorized" , 403
    available_bootcamps = Bootcamp.query.filter_by(status = 'Open').all()
    my_bookings = Booking.query.filter_by(user_id = current_user.id).all()
    return render_template('student_dashboard.html', bootcamps = available_bootcamps, bookings = my_bookings)

@login_required
@views.route('/book/<int:bootcamp_id>', methods = ['POST'])
def book_bootcamp(bootcamp_id):
    if current_user.role != 'student' : return "Unauthorized" , 403
    bootcamp = Bootcamp.query.get_or_404(bootcamp_id)

    if bootcamp.slots_available > 0 and bootcamp.status == 'Open':
        booking = Booking(user_id = current_user.id, bootcamp_id = bootcamp.id)
        bootcamp.slots_available -= 1
        db.session.add(booking)
        db.session.commit()
        flash('Bootcamp successsfully booked!', 'success')
    else:
        flash('Bootcamp is full or closed', 'danger')
    return redirect(url_for('views.student_dashboard'))


#API Endpoints 

@views.route('/api/bootcamps', methods = ['GET'])
def get_bootcamp():
    bootcamps = Bootcamp.query.all()
    data = []
    for b in bootcamps:
        data.append({
            'id' : b.id,
            'title' : b.title,
            'slots_available' : b.slots_available,
            'status' : b.status,
            'mentor_id' : b.mentor_id
        })
    return jsonify({'bootcamps' : data}), 200


@views.route('/api/bootcamps', methods = ['POST'])
def create_api_bootcamp():
    data = request.get_json()

    if not data or not data.get('title') or not data.get('slots_available'):
        return jsonify({'error' : 'Missing required fields'}), 400
    
    new_bootcamp = Bootcamp(title = data['title'],
                            slots_available = data['slots_available'],
                            status = data.get('status', 'Open')
    )

    db.session.add(new_bootcamp)
    db.session.commit()

    return jsonify({
        'message' : 'Bootcamp successfully created!',
        'bootcamp_id' : new_bootcamp.id
    }), 201