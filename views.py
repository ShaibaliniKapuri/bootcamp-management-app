from flask import Blueprint,render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Booking, Bootcamp


views = Blueprint('views', __name__)


#Admin Functionalities

@login_required
@views.route('/admin')
def admin_dashboard():
    if current_user.role != 'admin':
        return "unauthorized", 403
    
    bootcamps = Bootcamp.query.all()
    mentors = User.query.filter_by(role = 'mentor').all()
    students = User.query.filter_by(role = 'student').all()

    return render_template('admin_dashboard.html', bootcamps = bootcamps, mentors = mentors, students = students)


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


    