import os
print("Using DB:", os.path.abspath("recruitment.db"))
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
import threading  # ← ضيف هذا السطر
from werkzeug.utils import secure_filename
import time

# app.py
from routes.job_routes import bp as job_routes_bp

from flask import Flask

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruitment.db'  # تحديد المسار الصحيح إلى قاعدة البيانات
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # لتقليل التحذيرات من SQLAlchemy

app.secret_key = 'your-very-secret-key-123'  # مهم علشان flash و session

# باقي الدوال والراوتات
app.secret_key = 'your-very-secret-key-123'  # مهم علشان flash و session




# إعدادات الأمان
app.config['SECRET_KEY'] = 'your_secret_key_here'  # لا تنسى تغيير هذه القيمة


# قفل لضمان أن الوصول إلى قاعدة البيانات يتم بشكل متسلسل
db_lock = threading.Lock()



def get_db_connection():
    try:
        conn = sqlite3.connect('recruitment.db')
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')  # تأكد من تفعيل قيود العلاقات
        print("Database connected successfully!")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")  # إذا كان هناك خطأ في الاتصال
        return None



db_lock = threading.Lock()

def get_db_connection():
    with db_lock:
        conn = sqlite3.connect('recruitment.db')
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn



# ====== تحديث الجدول بإضافة الأعمدة المفقودة ======
def update_table():
    retries = 5
    for i in range(retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # تحقق من وجود الأعمدة المطلوبة في جدول applications
            cursor.execute("PRAGMA table_info(applications);")
            columns = [column[1] for column in cursor.fetchall()]

            # إضافة الأعمدة في حالة عدم وجودها
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
    print("تعذر إجراء التعديل بعد عدة محاولات.")

# استدعاء دالة تحديث الجدول لتأكد من إضافة الأعمدة الجديدة
update_table()

# ====== صفحات الواجهة العامة ======


UPLOAD_FOLDER = 'path_to_your_upload_folder'  # تأكد من ضبط مسار مجلد التحميل بشكل صحيح
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])


@app.route('/apply', methods=['POST'])
def apply():
    name = request.form['name']
    email = request.form['email']
    job_id = request.form['job_id']
    cv_text = request.form['cv_text']  # أو بترفع ملف PDF وتقرأه
    created_at = datetime.now()

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO applications (name, email, job_id, cv_text, created_at) VALUES (?, ?, ?, ?, ?)',
        (name, email, job_id, cv_text, created_at)
    )
    conn.commit()
    conn.close()

    return redirect('/thank_you')



@app.route('/start-interview/<int:application_id>')
def start_interview(application_id):
    print(f"Application ID: {application_id}")  # طباعة القيمة للتحقق
  
    # جلب بيانات المتقدم بناءً على application_id
    try:
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
        application = cursor.fetchone()
        
        # إذا لم يكن هناك طلب بهذا الـ application_id، إظهار رسالة خطأ
        if not application:
            return "الطلب غير موجود."
        
        # تحويل السجل إلى قاموس باستخدام الأسماء الصحيحة للأعمدة
        application_dict = dict(zip([column[0] for column in cursor.description], application))
        
        # استخراج السيرة الذاتية من التطبيق
        cv_path = application_dict['cv_path']
        
        # استخراج النص من السيرة الذاتية بناءً على نوع الملف
        if cv_path.endswith('.pdf'):
            cv_text = extract_text_from_pdf(cv_path)
        elif cv_path.endswith('.docx'):
            cv_text = extract_text_from_docx(cv_path)
        else:
            return "الملف غير مدعوم."
        
        # الحصول على الكلمات المفتاحية للوظيفة من قاعدة البيانات
        job_id = application_dict['job_id']
        cursor.execute('SELECT title, keywords FROM jobs WHERE id = ?', (job_id,))
        job = cursor.fetchone()
        
        if not job:
            return "الوظيفة غير موجودة."
        
        job_title, job_keywords = job
        job_keywords = job_keywords.split(',')  # إذا كانت الكلمات المفتاحية مفصولة بفواصل
        
        # تحليل السيرة الذاتية مقارنة بالكلمات المفتاحية الخاصة بالوظيفة
        match_percentage = analyze_cv_against_job(cv_text, job_keywords)
        
        # تخزين التقييم في قاعدة البيانات
        store_ai_evaluation(application_id, match_percentage)
        
        # إعادة توجيه المستخدم مع عرض النتيجة
        return render_template('interview_result.html', 
                               application=application_dict, 
                               match_percentage=match_percentage, 
                               job_title=job_title)

    except sqlite3.Error as e:
        return f"حدث خطأ في قاعدة البيانات: {e}"
    finally:
        conn.close()  # تأكد من إغلاق الاتصال





@app.route('/jobs')
def jobs():
    query = request.args.get('q', '')
    conn = get_db_connection()
    jobs_list = conn.execute("SELECT * FROM jobs WHERE title LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs_list, query=query)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # قم بتحديد المسار للمجلد الذي ترغب في تخزين الملفات فيه

# تأكد من أن المجلد موجود
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = '/path/to/upload/folder'  # تأكد من تحديد مجلد التحميل بشكل صحيح

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('home.html')
@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/seeker-profile')
def seeker_profile():
    return render_template('إعداد الملف الشخصي.html')

import os

@app.route('/employment-application', methods=['GET', 'POST'])
def employment_application():
    if request.method == 'POST':
        print("📥 Received POST /employment-application request")

        user_name = request.form.get('name')
        user_email = request.form.get('email')

        print("🧾 Received name:", user_name)
        print("📧 Received email:", user_email)

        cv_file = request.files.get('cvInput')
        cv_text = None
        file_path = None

        if cv_file:
            upload_folder = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, cv_file.filename)
            cv_file.save(file_path)

            # ممكن تضيف كود استخراج النص من الـ CV هنا لو حابب

        try:
            conn = sqlite3.connect('recruitment.db')
            c = conn.cursor()

            print("🛠️ Inserting into DB...")
            c.execute('''
                INSERT INTO applications (user_name, user_email, cv_text, cv_path)
                VALUES (?, ?, ?, ?)
            ''', (user_name, user_email, cv_text, file_path))

            conn.commit()
            print("✅ Insert successful!")

        except Exception as e:
            print("❌ DB Insert Error:", e)

        finally:
            conn.close()

        return redirect(url_for('application_success'))
    return render_template('employment_application.html')


@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM applications').fetchall()
    conn.close()
    return f"عدد الطلبات المسجلة: {len(data)}"


from flask import Flask, render_template, request, jsonify, redirect
import sqlite3

# تعديل دالة الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('recruitment.db', timeout=10)  # زيادة المهلة لتفادي قفل قاعدة البيانات
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("📥 دخلنا على /signup")  # Debug أول الصفحة

    try:
        if request.method == 'POST':
            print("📤 طلب POST")  # Debug POST

            # استخراج البيانات من النموذج
            user_type = request.form.get('user_type')
            username = request.form.get('username')
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')  # إضافة هنا

            print(f"Received role: {role}")

            print(f"🧾 البيانات المستلمة:\nنوع المستخدم: {user_type}\nاسم المستخدم: {username}\nالاسم: {full_name}\nالإيميل: {email}\nكلمة المرور: {password}")

            # التحقق من البريد الإلكتروني
            conn = get_db_connection()  # الاتصال بقاعدة البيانات
            cursor = conn.cursor()
            existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

            if existing_user:  # لو البريد الإلكتروني موجود مسبقًا
                conn.close()
                print("❌ البريد موجود مسبقًا")
                return jsonify({'success': False, 'message': 'البريد الإلكتروني موجود بالفعل. الرجاء اختيار بريد آخر.'})

            # إدخال المستخدم الجديد في قاعدة البيانات
            try:
                cursor.execute(''' 
                    INSERT INTO users (user_type, username, full_name, email, password, role) 
                    VALUES (?, ?, ?, ?, ?, ?) 
                ''', (user_type, username, full_name, email, password, role))
                conn.commit()
                print("✅ تم التسجيل بنجاح")
            except Exception as e:
                print(f"💥 خطأ أثناء إدخال البيانات في قاعدة البيانات: {e}")
                conn.rollback()  # التراجع في حالة الخطأ
                conn.close()
                return jsonify({'success': False, 'message': 'حدث خطأ أثناء التسجيل. يرجى المحاولة لاحقًا.'})

            conn.close()

            # إرسال الـ response مع التوجيه إلى صفحة الشكر
            return jsonify({'success': True, 'redirect': '/thankyou'})  # إرسال الـ redirect هنا

        return render_template('signup.html')

    except Exception as e:
        print(f"💥 خطأ أثناء التسجيل: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء التسجيل. يرجى المحاولة لاحقًا.'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
        conn.close()

        if user:
            # حفظ معلومات المستخدم في session
            session['user_id'] = user['id']
            session['username'] = user['username']
            print("✅ تسجيل الدخول ناجح")
            return redirect(url_for('dashboard'))  # توجه المستخدم للوحة التحكم
        else:
            print("❌ فشل تسجيل الدخول")
            return render_template('login.html', error='البريد الإلكتروني أو كلمة المرور غير صحيحة')

    return render_template('login.html')



@app.route('/thankyou')
def thankyou():
    print("🎉 تم الوصول إلى صفحة الشكر!")  # سجل دخول إلى الصفحة
    return render_template('thankyou.html')

@app.route('/thank-you')
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
 # تأكد من وجود الملف profile.html في مجلد templates
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

@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/application_success')
def application_success():
    return render_template('application_success.html')



# تأكد من استيراد الموديل الخاص بالتطبيقات
from models import Application  # استبدل هذا بالمسار الصحيح لموديل التطبيقات

def get_applications():
    # جلب جميع الطلبات من قاعدة البيانات
    applications = Application.query.all()  # أو استخدم استعلام حسب الحاجة
    return applications


app.secret_key = 'your-very-secret-key-123'  # مهم علشان flash و session

# الراوت لتحليل السيرة الذاتية
@app.route('/test_cv/<int:application_id>', methods=['GET'])
def test_cv(application_id):
    try:
        # الاتصال بقاعدة البيانات
        conn = get_db_connection()
        cursor = conn.cursor()

        # البحث عن التطبيق في قاعدة البيانات
        cursor.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
        application = cursor.fetchone()

        if not application:
            return jsonify({"message": "التطبيق غير موجود"}), 404

        # استخراج السيرة الذاتية والتعامل مع البيانات
        cv_text = application['cv_text']
        job_id = application['job_id']

        if not cv_text:
            return jsonify({"message": "لا توجد نصوص السيرة الذاتية"}), 400

        # التحليل باستخدام الذكاء الاصطناعي
        match_percentage = analyze_cv_against_job(cv_text, job_id)

        # إذا كانت النسبة غير معرفة أو 0، أضف تحقق إضافي
        if match_percentage is None:
            match_percentage = 0

        # تحديث حالة التقييم في قاعدة البيانات
        cursor.execute('UPDATE applications SET match_percentage = ? WHERE id = ?', (match_percentage, application_id))
        conn.commit()

        return jsonify({"match_percentage": match_percentage, "message": "تم الاختبار بنجاح"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "حدث خطأ أثناء معالجة طلبك"}), 500
    finally:
        conn.close()









@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/success_page')
def success_page():
    # جلب البيانات من قاعدة البيانات
    conn = get_db_connection()  # افترض أنك تستخدم هذه الدالة للاتصال بقاعدة البيانات
    applications = conn.execute('SELECT * FROM applications').fetchall()
    conn.close()

    # تمرير البيانات إلى القالب
    return render_template('employment_interviews.html', applications=applications)


@app.route('/employment_interviews')
def employment_interviews_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            applications.*, 
            ai_evaluations.match_percentage,
            jobs.title AS job_title
        FROM applications
        LEFT JOIN ai_evaluations ON applications.id = ai_evaluations.application_id
        LEFT JOIN jobs ON applications.job_id = jobs.id
        ORDER BY applications.created_at DESC
    """)
    applications = cursor.fetchall()

    conn.close()

    return render_template("employment_interviews.html", applications=applications)


@app.route('/start_interview/<int:application_id>', methods=['GET', 'POST'])
def start_interview(application_id):
    # التعامل مع البيانات الخاصة بـ application_id هنا
    return render_template('start_interview.html', application_id=application_id)

@app.route('/delete_application/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
            application = cursor.fetchone()

            if not application:
                flash("السجل غير موجود.", "error")
                return redirect(url_for('employment_interviews_page'))

            # حذف تقييمات الذكاء الاصطناعي المرتبطة إن وُجدت
            cursor = conn.execute('SELECT * FROM ai_evaluations WHERE application_id = ?', (application_id,))
            if cursor.fetchone():
                conn.execute('DELETE FROM ai_evaluations WHERE application_id = ?', (application_id,))

            # التحقق من وجود مقابلة مرتبطة
            cursor = conn.execute('SELECT * FROM interviews WHERE application_id = ?', (application_id,))
            if cursor.fetchone():
                flash("لا يمكن حذف هذا الطلب لأنه مرتبط بمقابلة.", "error")
                return redirect(url_for('employment_interviews_page'))

            # حذف الطلب
            conn.execute('DELETE FROM applications WHERE id = ?', (application_id,))
            conn.commit()

            flash("تم حذف الطلب بنجاح.", "success")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        flash("حدث خطأ أثناء حذف الطلب.", "error")

    return redirect(url_for('employment_interviews_page'))




from flask import Flask
from models import db  # استيراد db من models
from models import User, Job, Application, AIEvaluation, Interview  # استيراد النماذج

def create_app():
    
    from flask import Flask

    app.secret_key = 'your-very-secret-key-123'  # مهم علشان flash و session

# باقي الدوال والراوتات



    # تعيين إعدادات قاعدة البيانات مع المسار لقاعدة البيانات "recruitment.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruitment.db'  # تحديد المسار الصحيح
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # لتقليل التحذيرات

    # تهيئة SQLAlchemy مع التطبيق
    db.init_app(app)

    return app

# إنشاء التطبيق
app = create_app()

app.run(debug=True)


@app.route('/test-db')
def test_db():
    try:
        # التحقق من الاتصال بقاعدة البيانات
        first_record = Application.query.first()  # جلب أول سجل من جدول التطبيقات
        if first_record:
            return f"الاتصال بقاعدة البيانات ناجح! أول سجل: {first_record.name}"
        else:
            return "الاتصال بقاعدة البيانات ناجح ولكن لا توجد سجلات في جدول التطبيقات."
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {str(e)}"

    app.run(debug=True)



def calculate_cv_job_match(cv_text, job_description):
    # هنا تكتب منطق الحساب باستخدام الذكاء الاصطناعي
    # على سبيل المثال، باستخدام نموذج تحليل نصوص أو أي أداة أخرى
    match_percentage = 75  # مثال على حساب نسبة التطابق
    return match_percentage

from flask import render_template
from datetime import datetime



from flask import render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

app.secret_key = 'super-secret-key-change-this'

app.secret_key = 'your_secret_key'  # لا تنس تحديد مفتاح سري

csrf = CSRFProtect(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # إنشاء نموذج تسجيل الدخول
    if form.validate_on_submit():
        # قم بتنفيذ المنطق المناسب عند تقديم النموذج (مثل التحقق من بيانات المستخدم)
        return redirect(url_for('home'))  # على سبيل المثال، التوجيه إلى صفحة رئيسية
    return render_template('login.html', form=form)  # تمرير الفورم إلى القالب



# ====== استقبال طلب التوظيف ======






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

# استدعاء دالة إنشاء الجدول عند بداية تشغيل التطبيق
create_table()

# ====== تحديد إعدادات رفع الملفات ======
UPLOAD_FOLDER = 'uploads/cvs'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = 'uploads/cvs'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# دالة للتحقق من نوع الملف
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ====== دالة استقبال طلب التوظيف ======
# تحميل النموذج
from transformers import pipeline

model_name = 'bert-base-uncased'  # أو نموذج آخر مثل 'distilbert-base-uncased'
nlp = pipeline("zero-shot-classification", model=model_name)

def analyze_cv_against_job(cv_text, job_id):
    # تعريف الكلمات المفتاحية بناءً على ID الوظيفة
    job_keywords = {
        1: ["python", "machine learning", "ai", "deep learning", "data science"],  # مثال: مطور ذكاء اصطناعي
        2: ["figma", "ux", "design", "user interface", "prototype"],  # مثال: مصمم واجهات
    }

    # الحصول على الكلمات المفتاحية الخاصة بالوظيفة
    keywords = job_keywords.get(job_id, [])
    
    # حساب عدد المطابقات في النص
    matches = sum(1 for kw in keywords if kw.lower() in cv_text.lower())
    
    # حساب نسبة التوافق
    match_percentage = (matches / len(keywords)) * 100 if keywords else 0

    return match_percentage



def store_ai_evaluation(application_id, match_percentage):
    # الاتصال بقاعدة البيانات وتخزين النتيجة
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO ai_evaluations (application_id, evaluation_date, match_percentage, notes) 
                      VALUES (?, ?, ?, ?)''', 
                   (application_id, '2025-04-18', match_percentage, 'نسبة التوافق بين السيرة الذاتية والوظيفة'))
    conn.commit()
    conn.close()

def evaluate_application(application_id, job_description):
    # استرجاع السيرة الذاتية من قاعدة البيانات
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT cv_path FROM applications WHERE id = ?''', (application_id,))
    cv_path = cursor.fetchone()[0]
    
    # استخراج النص من السيرة الذاتية (إذا كانت PDF أو DOCX)
    with open(cv_path, 'r') as file:
        cv_text = file.read()

    # تحليل السيرة الذاتية مع الوصف الوظيفي
    match_percentage = analyze_cv_against_job(cv_text, job_description)
    
    # تخزين التقييم
    store_ai_evaluation(application_id, match_percentage)
    conn.close()

@app.route('/analyze_application/<int:application_id>')
def analyze_application(application_id):
    # الحصول على الوصف الوظيفي من قاعدة البيانات
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM jobs WHERE id = (SELECT job_id FROM applications WHERE id = ?)", (application_id,))
    job_title = cursor.fetchone()[0]

    # الوصف الوظيفي (يمكنك تخصيص هذا أكثر حسب الحاجة)
    job_description = f"مطور ويب، معرفة قوية بـ {job_title}"
    
    # استدعاء دالة تحليل السيرة الذاتية
    evaluate_application(application_id, job_description)

    return f"تم تحليل السيرة الذاتية للمتقدم {application_id} بنجاح"


# ====== دالة استقبال طلب التوظيف ======




from flask import render_template, redirect, url_for, request
import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'path/to/upload/directory'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # التأكد من السماح بالملفات الصحيحة

# التحقق من امتداد الملف
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from cv_parser import extract_text_from_pdf, extract_text_from_docx
from ai_analysis import analyze_cv_against_keywords
from database_ops import store_ai_evaluation


import sqlite3

# الدالة لإضافة وظيفة جديدة
def add_job():
    conn = sqlite3.connect('recruitment.db')  
    cursor = conn.cursor()
    cursor.execute(""" 
    INSERT INTO jobs (title, description, department, location, requirements, posted_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("مطور ويب", "تطوير تطبيقات الويب", "تكنولوجيا", "القاهرة", "خبرة في React و Python", "2025-04-18"))
    conn.commit()
    conn.close()

# الدالة لإضافة تطبيق جديد
def add_application():
    conn = sqlite3.connect('recruitment.db')  
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO applications (name, nationality, birth_date, religion, gender, marital_status, address, phone, currently_employed, interview_status, interview_date, interview_time, cv_path, job_id, match_percentage)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("أحمد علي", "مصر", "1990-01-01", "مسلم", "ذكر", "أعزب", "الجيزة", "0123456789", "نعم", "منتظر", "2025-04-20", "10:00", "/path/to/cv.pdf", 1, 80))
    conn.commit()
    conn.close()

# الدالة لإضافة تقييم ذكي
def add_ai_evaluation():
    conn = sqlite3.connect('recruitment.db')  
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ai_evaluations (application_id, evaluation_date, match_percentage, notes)
    VALUES (?, ?, ?, ?)
    """, (1, "2025-04-18", 85, "الذكاء الاصطناعي قام بتحليل السيرة الذاتية ووجد تطابقًا جيدًا"))
    conn.commit()
    conn.close()


# الدالة لإضافة مقابلة
def add_interview():
    conn = sqlite3.connect('recruitment.db')  
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO interviews (application_id, interviewer, interview_date, interview_time, notes, result)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (1, "محمود عبد الله", "2025-04-20", "10:00", "مقابلة جيدة مع المهارات التقنية المطلوبة", "مقبول"))
    conn.commit()
    conn.close()

# الدالة لإضافة مستخدم
def add_user():
    conn = sqlite3.connect('recruitment.db')  
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (username, password, role)
    VALUES (?, ?, ?)
    """, ("admin", "admin123", "مدير"))
    conn.commit()
    conn.close()

# دالة لعرض جميع البيانات
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

    print(app.url_map)


# استدعاء دالة إضافة الوظيفة (يمكنك استدعاء الدوال الأخرى حسب الحاجة)
add_job()

# لعرض جميع البيانات من الجداول
show_all_data()

# ====== تشغيل التطبيق ======
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
