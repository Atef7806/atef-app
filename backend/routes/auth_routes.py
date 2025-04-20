from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user

bp = Blueprint('auth_routes', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # منطق تسجيل الدخول
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # تحقق من صحة البيانات
        return redirect(url_for('job_routes.get_jobs'))

    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_routes.login'))
