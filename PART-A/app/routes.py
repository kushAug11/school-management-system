from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .forms import LoginForm
from main import validate_login, get_nursery_sections, get_inventory, process_purchase, get_history

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if validate_login(form.email.data, form.pwd.data):
            return redirect(url_for('main_bp.dashboard'))
        flash("Invalid Credentials")
    return render_template('login.html', form=form)

@main_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' not in session: return redirect(url_for('main_bp.login'))
    
    selected_sec = request.args.get('section_name')
    if request.method == 'POST':
        process_purchase(session['user_email'], request.form['plant_name'], 
                         request.form['qty'], request.form['section_name'])
        return redirect(url_for('main_bp.dashboard'))

    sections = get_nursery_sections()
    inventory = get_inventory(selected_sec)
    return render_template('nursery.html', sections=sections, inventory=inventory, 
                           selected_sec=selected_sec, user_name=session['user_name'])

@main_bp.route('/history')
def history():
    if 'loggedin' not in session: return redirect(url_for('main_bp.login'))
    orders = get_history(session['user_email'])
    return render_template('history.html', orders=orders, user_name=session['user_name'])

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_bp.login'))
