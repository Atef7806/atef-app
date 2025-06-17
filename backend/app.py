import os
import sqlite3
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import docx
from flask_login import LoginManager, current_user
from models import db, Application, User, Job, AIEvaluation, Interview
from routes.job_routes import bp as job_routes_bp
from routes.auth_routes import auth_bp
from routes.application_routes import bp as application_routes_bp
from routes.ai_analysis import analyze_cv_against_keywords
from flask_mail import Mail, Message  # ✅ هنا سطر واحد بس

# إنشاء التطبيق
app = Flask(__name__)

# إعدادات التطبيق
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recruitment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# إعدادات البريد الإلكتروني
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'eisd7954@gmail.com'  # غيره لبريدك
app.config['MAIL_PASSWORD'] = 'tyxa cshx wwlb pgiu'        # غيره لكلمة السر
app.config['MAIL_ASCII_ATTACHMENTS'] = False
from flask_mail import Message
from email.header import Header
mail = Mail(app)
# تهيئة قاعدة البيانات
db.init_app(app)

# إعدادات الملفات
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# قفل للوصول المتزامن
db_lock = threading.Lock()

# تهيئة Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# تسجيل Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(job_routes_bp)
app.register_blueprint(application_routes_bp, url_prefix='/applications')

# تعريف user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# === دوال مساعدة ===
def get_db_connection():
    with db_lock:
        conn = sqlite3.connect('recruitment.db')
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "".join(page.extract_text() for page in reader.pages)

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def analyze_cv_against_job(cv_text, job_keywords):
    matches = sum(1 for kw in job_keywords if kw.lower() in cv_text.lower())
    match_percentage = (matches / len(job_keywords)) * 100 if job_keywords else 0
    return match_percentage

def store_ai_evaluation(application_id, match_percentage):
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO ai_evaluations (application_id, evaluation_date, match_percentage, notes) 
                      VALUES (?, ?, ?, ?)''', 
                   (application_id, datetime.now().date(), match_percentage, 'تحليل تطابق السيرة الذاتية'))
    conn.commit()
    conn.close()

# ====== تحديث وإنشاء الجداول ======
def update_table():
    retries = 5
    for _ in range(retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(applications);")
            columns = [column[1] for column in cursor.fetchall()]
            if 'cv_path' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN cv_path TEXT;")
                conn.commit()
            if 'match_percentage' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN match_percentage REAL;")
                conn.commit()
            if 'job_id' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN job_id INTEGER;")
                conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            print(f"خطأ أثناء التعديل: {e}")
            time.sleep(2)

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        nationality TEXT,
        birth_date TEXT,
        religion TEXT,
        gender TEXT,
        marital_status TEXT,
        address TEXT,
        phone TEXT NOT NULL,
        currently_employed TEXT,
        interview_status TEXT,
        interview_date TEXT,
        interview_time TEXT,
        cv_path TEXT,
        created_at DATETIME
    )
    ''')
    conn.commit()
    conn.close()

# ====== تنفيذ التحديثات عند بداية التشغيل ======
update_table()
create_table()

# ====== الراوتات العامة ======
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/seeker_profile')
def seeker_profile():
    return render_template('seeker_profile.html')


@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/who-are-you')
def who_are_you():
    return render_template('who are you.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact us.html')
@app.route('/job-management')
def job_management():
    return render_template('job management.html')

@app.route('/manage-applicants')
def manage_applicants():
    return render_template('manage applicants.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/smart-search')
def smart_search():
    return render_template('smart search.html')

@app.route('/account-management')
def account_management():
    return render_template('account management.html')

@app.route('/advertisements')
def advertisements():
    return render_template('advertisements.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/customer-support')
def customer_support():
    return render_template('costomer support.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/application_success')
def application_success():
    return render_template('application_success.html')

@app.route('/jobs')
def jobs():
    query = request.args.get('q', '')
    conn = get_db_connection()
    jobs_list = conn.execute("SELECT * FROM jobs WHERE title LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs_list, query=query)

# ======= دالة التقديم على الوظيفة =======
@app.route('/employment-application', methods=['GET', 'POST'])
def employment_application():
    if request.method == 'POST':
        user_name = current_user.username if current_user.is_authenticated else request.form.get('name')
        user_email = current_user.email if current_user.is_authenticated else request.form.get('email')
        cv_file = request.files.get('cvInput')
        job_id = request.form.get('jobId')
        selected_job = request.form.get('selectedJob')
        job_requirements = request.form.get('jobRequirements')

        cv_text = None
        file_path = None

        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        if cv_file and allowed_file(cv_file.filename):
            filename = secure_filename(cv_file.filename)
            file_path = os.path.join(upload_folder, filename)
            cv_file.save(file_path)

            if filename.endswith('.pdf'):
                cv_text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                cv_text = extract_text_from_docx(file_path)
        else:
            flash('الرجاء رفع ملف بصيغة PDF أو DOCX فقط.', 'error')
            return redirect(request.url)

        try:
            conn = sqlite3.connect('recruitment.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO applications 
                (user_name, user_email, cv_text, cv_path, created_at, selected_job, job_requirements, job_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_name, user_email, cv_text, file_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), selected_job, job_requirements, job_id))
            conn.commit()
        except Exception as e:
            print("❌ DB Insert Error:", e)
            flash('حدث خطأ أثناء حفظ بياناتك.', 'error')
            return redirect(request.url)
        finally:
            conn.close()

        flash('تم تقديم طلبك بنجاح!', 'success')
        return redirect(url_for('application_success'))

    return render_template('employment_application.html')

# ======= دالة بدء المقابلة =======
@app.route('/start-interview/<int:application_id>')
def start_interview(application_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
        application = cursor.fetchone()

        if not application:
            return "الطلب غير موجود."

        application_dict = dict(zip([column[0] for column in cursor.description], application))
        cv_path = application_dict['cv_path']

        if cv_path.endswith('.pdf'):
            cv_text = extract_text_from_pdf(cv_path)
        elif cv_path.endswith('.docx'):
            cv_text = extract_text_from_docx(cv_path)
        else:
            return "الملف غير مدعوم."

        job_id = application_dict.get('job_id')
        if not job_id:
            return "لم يتم تحديد وظيفة لهذا الطلب."

        cursor.execute('SELECT title, requirements FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()

        if not job:
            return "الوظيفة غير موجودة."

        job_title, job_requirements = job
        job_keywords = job_requirements.split(',') if job_requirements else []

        match_percentage = analyze_cv_against_job(cv_text, job_keywords)
        store_ai_evaluation(application_id, match_percentage)

        return render_template('interview_result.html',
                               application=application_dict,
                               match_percentage=match_percentage,
                               job_title=job_title)

    except sqlite3.Error as e:
        return f"حدث خطأ في قاعدة البيانات: {e}"
    finally:
        conn.close()


# ======= دالة تقييم الطلب بناء على الوظيفة =======
def evaluate_application(application_id, job_description):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT cv_path FROM applications WHERE id = ?', (application_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise Exception(f"لم يتم العثور على التطبيق برقم {application_id}")

    cv_path = result['cv_path']

    if not os.path.exists(cv_path):
        conn.close()
        raise Exception(f"ملف السيرة الذاتية غير موجود: {cv_path}")

    if cv_path.endswith('.pdf'):
        cv_text = extract_text_from_pdf(cv_path)
    elif cv_path.endswith('.docx'):
        cv_text = extract_text_from_docx(cv_path)
    else:
        conn.close()
        raise Exception("صيغة ملف السيرة الذاتية غير مدعومة.")

    match_percentage = analyze_cv_against_job(cv_text, job_description)
    store_ai_evaluation(application_id, match_percentage)
    conn.close()


# ======= دالة اختبار السيرة الذاتية =======
@app.route('/test_cv/<int:application_id>', methods=['GET'])
def test_cv(application_id):
    try:
        conn = sqlite3.connect('recruitment.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
        application = cursor.fetchone()

        if not application:
            return jsonify({"message": "التطبيق غير موجود"}), 404

        cv_text = application['cv_text']
        job_requirements = application['job_requirements']
        email = application['user_email']

        if not cv_text or not job_requirements:
            return jsonify({"message": "لا توجد نصوص السيرة الذاتية أو متطلبات الوظيفة"}), 400

        requirements_list = [req.strip() for req in job_requirements.split(',') if req.strip()]
        match_percentage = analyze_cv_against_keywords(cv_text, requirements_list)

        cursor.execute('UPDATE applications SET match_percentage = ? WHERE id = ?', (match_percentage, application_id))
        conn.commit()

        # لو مؤهل بنسبة كبيرة (مثلا 80%)
        if match_percentage >= 80:
            send_acceptance_email(email, application['selected_job'])

        return jsonify({
          "match_percentage": round(match_percentage, 2),
           "message": "تم الاختبار بنجاح باستخدام الذكاء الاصطناعي"
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "حدث خطأ أثناء معالجة طلبك"}), 500
    finally:
        conn.close()

from email.header import Header

def send_acceptance_email(email, job_title):
    subject = str(Header('مبروك! تم قبولك في وظيفة {}'.format(job_title), 'utf-8'))
    body = f"""مبروك 🎉

لقد تم قبولك في وظيفة: {job_title}

سنتواصل معك قريبًا لتحديد موعد المقابلة أو بدء العمل.

بالتوفيق دائمًا!
"""

    msg = Message(
        recipients=[email],
        sender=current_app.config['MAIL_USERNAME'],
    )

    msg.subject = subject
    msg.body = body

    mail.send(msg)

# ======= دالة عرض المقابلات =======
@app.route('/employment_interviews')
def employment_interviews_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            applications.*, 
            ai_evaluations.match_percentage,
            jobs.title AS job_title
        FROM applications
        LEFT JOIN ai_evaluations ON applications.id = ai_evaluations.application_id
        LEFT JOIN jobs ON applications.job_id = jobs.id
        ORDER BY applications.created_at DESC
    ''')
    applications = cursor.fetchall()
    conn.close()

    return render_template("employment_interviews.html", applications=applications)

@app.route('/delete_application/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
            application = cursor.fetchone()

            if not application:
                flash("السجل غير موجود.", "error")
                return redirect(url_for('employment_interviews_page'))

            cursor = conn.execute('SELECT * FROM ai_evaluations WHERE application_id = ?', (application_id,))
            if cursor.fetchone():
                conn.execute('DELETE FROM ai_evaluations WHERE application_id = ?', (application_id,))

            cursor = conn.execute('SELECT * FROM interviews WHERE application_id = ?', (application_id,))
            if cursor.fetchone():
                flash("لا يمكن حذف هذا الطلب لأنه مرتبط بمقابلة.", "error")
                return redirect(url_for('employment_interviews_page'))

            conn.execute('DELETE FROM applications WHERE id = ?', (application_id,))
            conn.commit()

            flash("تم حذف الطلب بنجاح.", "success")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        flash("حدث خطأ أثناء حذف الطلب.", "error")

    return redirect(url_for('employment_interviews_page'))

# ====== دوال الإضافة اليدوية ======

def add_job():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute(""" 
    INSERT INTO jobs (title, description, department, location, requirements, posted_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("مطور ويب", "تطوير تطبيقات الويب", "تكنولوجيا", "القاهرة", "خبرة في React و Python", "2025-04-18"))
    conn.commit()
    conn.close()

def add_application():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO applications (name, nationality, birth_date, religion, gender, marital_status, address, phone, currently_employed, interview_status, interview_date, interview_time, cv_path, job_id, match_percentage)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("أحمد علي", "مصر", "1990-01-01", "مسلم", "ذكر", "أعزب", "الجيزة", "0123456789", "نعم", "منتظر", "2025-04-20", "10:00", "/path/to/cv.pdf", 1, 80))
    conn.commit()
    conn.close()

def add_ai_evaluation():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ai_evaluations (application_id, evaluation_date, match_percentage, notes)
    VALUES (?, ?, ?, ?)
    """, (1, "2025-04-18", 85, "تحليل ذكاء اصطناعي للسيرة الذاتية"))
    conn.commit()
    conn.close()

def add_interview():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO interviews (application_id, interviewer, interview_date, interview_time, notes, result)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (1, "محمود عبد الله", "2025-04-20", "10:00", "مقابلة تقنية ممتازة", "مقبول"))
    conn.commit()
    conn.close()

def add_user():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (username, password, role)
    VALUES (?, ?, ?)
    """, ("admin", "admin123", "مدير"))
    conn.commit()
    conn.close()
def show_all_data():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"\nالبيانات في جدول {table_name}:")
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print(f"الجدول {table_name} فارغ أو لا يحتوي على بيانات.")
    conn.close()

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM applications').fetchall()
    conn.close()
    return f"عدد الطلبات المسجلة: {len(data)}"

def get_applications():
    applications = Application.query.all()
    return applications

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
# نهاية الملف

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # التحقق من وجود البريد الإلكتروني وكلمة المرور في قاعدة البيانات
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            # تخزين بيانات المستخدم في الجلسة
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']

            # إعادة توجيه المستخدم إلى الصفحة الشخصية
            return redirect(url_for('profile'))

        else:
            # عرض رسالة الخطأ
            return render_template('login.html', error="البريد الإلكتروني أو كلمة المرور غير صحيحة")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # التأكد من البيانات المدخلة
        if not email or not username or not password or not role:
            return jsonify({'success': False, 'message': 'الرجاء تعبئة جميع الحقول المطلوبة.'})

        # الاتصال بقاعدة البيانات
        conn = get_db_connection()
        cursor = conn.cursor()
        existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user:
            conn.close()
            return jsonify({'success': False, 'message': 'البريد الإلكتروني موجود بالفعل.'})

        cursor.execute('''INSERT INTO users (user_type, username, full_name, email, password, role) 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (user_type, username, full_name, email, password, role))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'redirect': '/thank_you'})  # إعادة التوجيه لصفحة الشكر

    return render_template('signup.html')




# ====== تشغيل التطبيق ======
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
