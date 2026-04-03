from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from main import (
    validate_admin, get_admin_name, validate_educator_details, 
    add_educator_details, update_educator_details, 
    get_students_on_status, update_application, withdraw_application,
    user_login, apply_application, 
    check_attendance, start_attendance, stop_attendance, mark_attendance,
    get_attendance_list, get_students_attendance,
    educator, applicant
)

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/index')
def home_index():
    return render_template('index.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_bp.admin_login'))

# ==========================================
# Application Portal
# ==========================================
@main_bp.route('/application_portal/home')
def application_home():
    return render_template('Application Portal/application_home.html')

@main_bp.route('/application_portal/apply', methods=['GET', 'POST'])
def application_apply():
    from app.form_impl import RegistrationForm
    form = RegistrationForm()
    
    if form.validate_on_submit():
        apply_application({
            "name": form.name.data,
            "email": form.email.data,
            "dob": form.dob.data.strftime("%Y-%m-%d"),
            "guardian_name": form.guardian_name.data,
            "guardian_contact": form.guardian_contact.data,
            "language1": form.language1.data,
            "language2": form.language2.data,
            "math": form.math.data,
            "science": form.science.data,
            "history": form.history.data,
            "geography": form.geography.data,
        })
        flash("Application successfully submitted.")
        return redirect(url_for('main_bp.application_status'))
        
    return render_template('Application Portal/register.html', form=form)

@main_bp.route('/application_portal/status', methods=['GET', 'POST'])
def application_status():
    status = None
    if request.method == 'POST':
        email = request.form.get('email')
        app = next((a for a in applicant if a["email"] == email), None)
        if app:
            status = app["status"]
            session['applicant_email'] = email
        else:
            flash("No application found for this email.")
    return render_template('Application Portal/application_status.html', status=status, applicant_email=session.get('applicant_email'))

@main_bp.route('/application_portal/withdraw', methods=['POST'])
def view_withdraw_application():
    email = request.form.get('email')
    if email:
        res = withdraw_application(email)
        if res == 0:
            flash("Application withdrawn")
            session.pop('applicant_email', None)
        else:
            flash("Email not found in applications.")
    return redirect(url_for('main_bp.application_home'))

# ==========================================
# Attendance Management
# ==========================================
@main_bp.route('/attendance/login', methods=['GET', 'POST'])
def attendance_login():
    if request.method == 'POST':
        role = request.form.get('user_role')
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        res = user_login(role, user_name, password)
        
        if isinstance(res, int):
            if res in [1, 2, 3]: flash("Educator login failed")
            elif res in [4, 5]: flash("Student login failed")
            else: flash("Invalid Role")
        else:
            session['user'] = res # Usually the Name returned
            session['role'] = role
            
            if role == 'educator':
                edu = next((e for e in educator if e["user_name"] == user_name), None)
                if edu: session['user_id'] = edu["edu_id"]
                return redirect(url_for('main_bp.attendance_start_page'))
            else:
                student = next((a for a in applicant if a["email"] == user_name), None)
                if student: session['student_id'] = student["id"]
                session['student_name'] = res
                return redirect(url_for('main_bp.attendance_mark'))
    return render_template('Attendance Management/user_login.html')

@main_bp.route('/attendance/start_page', methods=['GET'])
def attendance_start_page():
    return render_template('Attendance Management/start_attendance.html', educator_name=session.get('user'))

@main_bp.route('/attendance/start', methods=['POST'])
def start_attendance_route():
    edu_id = session.get('user_id', 1)
    res = start_attendance(edu_id)
    if res == 1:
        flash("Another attendance is currently ongoing!")
    elif res == 2:
        flash("You already started an attendance collection today!")
    else:
        flash("Attendance started successfully.")
    return redirect(url_for('main_bp.attendance_start_page'))

@main_bp.route('/attendance/stop', methods=['POST'])
def stop_attendance_route():
    res = stop_attendance()
    if res == 1:
        flash("No attendance collection is currently ongoing!")
    else:
        flash("Attendance stopped successfully.")
    return redirect(url_for('main_bp.attendance_start_page'))

@main_bp.route('/attendance/mark', methods=['GET', 'POST'])
def attendance_mark():
    if request.method == 'POST':
        student_id = session.get('student_id')
        if not student_id:
            flash("Please log in as student first.")
            return redirect(url_for('main_bp.attendance_login'))
            
        res = mark_attendance(student_id)
        if res == 1:
            flash("No ongoing attendance collection from educator!")
        elif res == 2:
            flash("You have already marked your attendance!")
        else:
            flash("Attendance marked successfully.")
    return render_template('Attendance Management/attendance_marking.html', student_name=session.get('student_name'))

@main_bp.route('/attendance/view')
def view_attendance():
    logs = get_attendance_list()
    return render_template('Attendance Management/view_attendance.html', attendance_logs=logs)

@main_bp.route('/attendance/view/<int:id>')
def view_attendance_detail(id):
    res = get_students_attendance(id)
    if isinstance(res, int) and res == 1:
        flash("Cannot view details for an ongoing attendance collection!")
        # Fallback to main view
        logs = get_attendance_list()
        return render_template('Attendance Management/view_attendance.html', attendance_logs=logs)
    
    # We pass 'student_logs' to the same template or perhaps render a different table for details?
    # Need to check view_attendance.html to see what it's expecting for detail view!
    logs = get_attendance_list()
    return render_template('Attendance Management/view_attendance.html', attendance_logs=logs, student_details=res, detail_id=id)


# ==========================================
# Resource Management
# ==========================================
@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user_name = request.form.get('admin_name')
        pwd = request.form.get('password')
        res = validate_admin(user_name, pwd)
        if res == 1:
            flash("Username not found")
        elif res == 2:
            flash("Incorrect Password")
        elif res == 0:
            name_res = get_admin_name(user_name)
            session['admin'] = name_res if isinstance(name_res, str) else "Admin"
            return redirect(url_for('main_bp.admin_home'))
    return render_template('Resource Management/admin_login.html')

@main_bp.route('/admin/home')
def admin_home():
    return render_template('Resource Management/admin_home.html')

@main_bp.route('/admin/educator', methods=['GET', 'POST'])
def educator_management():
    return render_template('Resource Management/educator_management.html')

@main_bp.route('/admin/admission', methods=['GET', 'POST'])
def admission_management():
    apps = get_students_on_status('new')
    return render_template('Resource Management/admission_management.html', applications=apps)

@main_bp.route('/admin/admission/accept/<int:id>', methods=['POST'])
def accept_application_route(id):
    res = update_application(id, 'accept')
    if res == 0:
        flash("Application accepted")
    else:
        flash(f"Error {res} updating application.")
    return redirect(url_for('main_bp.admission_management'))

@main_bp.route('/admin/admission/reject/<int:id>', methods=['POST'])
def reject_application_route(id):
    res = update_application(id, 'reject')
    if res == 0:
        flash("Application rejected")
    else:
        flash(f"Error {res} updating application.")
    return redirect(url_for('main_bp.admission_management'))
