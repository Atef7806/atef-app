from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, Application
from cv_parser import extract_text_from_pdf, extract_text_from_docx  # تأكد من استيراد الدوال بشكل صحيح

bp = Blueprint('application_routes', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# التأكد من أن الملف مسموح به
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# دالة تقديم الطلب
# التوجيه إلى صفحة النجاح بعد تقديم الطلب
@app.route('/submit_application', methods=['POST'])
def submit_application():
    # استخراج البيانات من النموذج
    user_name = request.form['name']
    user_email = request.form['email']
    job_id = request.form['job_id']

    # التحقق من رفع السيرة الذاتية
    uploaded_file = request.files.get('cv_file')
    if not uploaded_file or not allowed_file(uploaded_file.filename):
        flash('يرجى رفع سيرة ذاتية بصيغة pdf أو docx.', 'error')
        return redirect(url_for('application_routes.submit_application'))  # إعادة التوجيه إذا لم يتم رفع السيرة الذاتية

    # حفظ السيرة الذاتية في المجلد
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    filename = secure_filename(uploaded_file.filename)
    cv_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(cv_path)

    # استخراج النص من السيرة الذاتية
    cv_text = ""
    if filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(cv_path)
    elif filename.endswith('.docx'):
        cv_text = extract_text_from_docx(cv_path)

    # إنشاء الطلب وإضافته إلى قاعدة البيانات
    application = Application(
        user_name=user_name,
        user_email=user_email,
        cv_text=cv_text,
        cv_path=cv_path,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    flash("تم تقديم الطلب بنجاح", "success")

    # توجيه المستخدم إلى صفحة النجاح بعد تقديم الطلب
    return redirect(url_for('application_routes.application_success'))  # تأكد من التوجيه الصحيح هنا

# صفحة النجاح بعد تقديم الطلب
@app.route('/application_success')
def application_success():
    return render_template('application_success.html')  # تأكد من أن الملف موجود في مجلد templates
