from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import threading
import time
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# قفل لضمان أن الوصول إلى قاعدة البيانات يتم بشكل متسلسل
db_lock = threading.Lock()

# ====== قاعدة البيانات ======
def get_db_connection():
    with db_lock:
        conn = sqlite3.connect('database.db', timeout=60)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

# ====== تحديث الجدول بإضافة الأعمدة المفقودة ======
def update_table():
    retries = 5
    for i in range(retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # تحقق من وجود العمود قبل إضافته
            cursor.execute("PRAGMA table_info(applications);")
            columns = [column[1] for column in cursor.fetchall()]

            if 'cv_path' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN cv_path TEXT;")
                conn.commit()

            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE applications ADD COLUMN created_at DATETIME;")
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
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/jobs')
def jobs():
    query = request.args.get('q', '')
    jobs_list = [
        {
            "title": "مطور ذكاء اصطناعي",
            "company": "شركة المستقبل",
            "image": "https://source.unsplash.com/random/800x600?ai",
            "salary": "25,000 - 30,000 ر.س",
            "location": "الرياض",
            "tags": ["AI", "Python", "Machine Learning"],
            "description": "تطوير أنظمة الذكاء الاصطناعي المتقدمة"
        },
    ]
    results = [job for job in jobs_list if query in job['title']] if query else jobs_list
    return render_template('jobs.html', jobs=results, query=query)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/seeker-profile')
def seeker_profile():
    return render_template('الملف الشخصي للباحث عن عمل.html')

@app.route('/employment-application')
def employment_application():
    return render_template('employment_application.html')

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

@app.route('/employment_interviews')
def employment_interviews_page():
    conn = get_db_connection()
    applications = conn.execute("SELECT * FROM applications").fetchall()
    conn.close()

    # تحويل السجلات إلى قائمة من القواميس
    applications_list = []
    for application in applications:
        application_dict = dict(application)
        try:
            application_dict['created_at'] = datetime.strptime(application_dict['created_at'], "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            application_dict['created_at'] = datetime.strptime(application_dict['created_at'], "%Y-%m-%d %H:%M:%S")
        applications_list.append(application_dict)

    return render_template('employment_interviews.html', applications=applications_list)


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

@app.route('/log-out')
def log_out():
    return render_template('log out.html')

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

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# دالة للتحقق من نوع الملف
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====== دالة استقبال طلب التوظيف ======
@app.route('/submit-application', methods=['POST'])
def submit_application():
    try:
        data = request.form

        # استخراج البيانات من النموذج
        name = data.get('fullName') or data.get('name')
        phone = data.get('phone')
        nationality = data.get('nationality')
        birth_date = data.get('birthDate')
        religion = data.get('religion')
        gender = data.get('gender')
        marital_status = data.get('maritalStatus')
        address = data.get('address')
        currently_employed = data.get('currentlyEmployed')

        interview_status = data.get('interviewStatus')
        interview_date = data.get('interviewDate')
        interview_time = data.get('interviewTime')

        # التعامل مع ملف السيرة الذاتية
        file = request.files.get('cvInput')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"تم حفظ السيرة الذاتية في {file_path}")
        else:
            return "لا يوجد ملف مرفق أو نوع الملف غير مدعوم"

        conn = get_db_connection()
        cursor = conn.cursor()

        # التحقق من وجود طلب مسبق بنفس الاسم ورقم الهاتف
        existing = cursor.execute("SELECT * FROM applications WHERE name = ? AND phone = ?", (name, phone)).fetchone()
        if existing:
            conn.close()
            return "<h3 style='color:green;'>تم إرسال طلبك سابقًا، نحن بالفعل نستعرضه ✅</h3>"

        cursor.execute(''' 
            INSERT INTO applications 
            (name, nationality, birth_date, religion, gender, marital_status, address, phone, currently_employed, interview_status, interview_date, interview_time, cv_path, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            nationality,
            birth_date,
            religion,
            gender,
            marital_status,
            address,
            phone,
            currently_employed,
            interview_status,
            interview_date,
            interview_time,
            file_path,  # مسار السيرة الذاتية
            datetime.utcnow()  # إضافة التاريخ والوقت الحاليين
        ))

        conn.commit()
        conn.close()

        return render_template('application_submitted.html')

    except Exception as e:
        print(f"خطأ أثناء الحفظ: {e}")
        return "حدث خطأ أثناء إرسال الطلب"

# ====== دالة حذف طلب التوظيف ======
@app.route('/delete_application/<int:application_id>', methods=['GET'])
def delete_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # حذف السجل بناءً على ID
    cursor.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    conn.commit()

    # إغلاق الاتصال
    conn.close()

    # إعادة التوجيه إلى صفحة المقابلات بعد الحذف
    return redirect(url_for('employment_interviews_page'))

# ====== تشغيل التطبيق ======
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
