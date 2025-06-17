from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, Application, Job
from routes.cv_parser import extract_text_from_pdf, extract_text_from_docx

bp = Blueprint('application_routes', __name__)

# أنواع الملفات المسموح بها
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# دالة التأكد أن الملف له امتداد مسموح
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# دالة تقديم الطلب
@bp.route('/submit_application/<int:job_id>', methods=['POST'])
def submit_application(job_id):
    if not current_user.is_authenticated:
        flash("يجب عليك التسجيل أو تسجيل الدخول للتقديم على الوظيفة.", "error")
        return redirect(url_for('auth.signup'))
    
    user_name = current_user.username
    user_email = current_user.email

    uploaded_file = request.files.get('cv_file')
    if not uploaded_file or not allowed_file(uploaded_file.filename):
        flash('يرجى رفع سيرة ذاتية بصيغة PDF أو DOCX.', 'error')
        return redirect(url_for('job_routes.jobs'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = secure_filename(uploaded_file.filename)
    cv_path_full = os.path.join(upload_folder, filename)  # المسار الكامل لحفظ الملف
    uploaded_file.save(cv_path_full)

    # استخراج نص السيرة الذاتية
    cv_text = ""
    if filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(cv_path_full)
    elif filename.endswith('.docx'):
        cv_text = extract_text_from_docx(cv_path_full)

    if not cv_text:
        cv_text = "لم يتم استخراج نص من السيرة الذاتية."

    # جلب بيانات الوظيفة
    job = Job.query.get_or_404(job_id)

    # إنشاء سجل التقديم
    application = Application(
        user_name=user_name,
        user_email=user_email,
        cv_text=cv_text,
        cv_path=os.path.join('uploads', filename),  # المسار النسبي فقط ليظهر الملف
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        job_id=job_id
    )

    try:
        db.session.add(application)
        db.session.commit()
        flash("تم تقديم الطلب بنجاح!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء تقديم الطلب: {e}", "error")

    return redirect(url_for('application_routes.application_success'))

# صفحة نجاح التقديم
@bp.route('/application_success')
def application_success():
    return render_template('application_success.html')

# عرض جميع الطلبات في صفحة المقابلات للمدير
@bp.route('/interviews')
def view_interviews():
    applications = Application.query.all()
    return render_template('employment_interviews.html', applications=applications)
