from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import threading

app = Flask(__name__)

# قفل لضمان أن الوصول إلى قاعدة البيانات يتم بشكل متسلسل
db_lock = threading.Lock()

# ====== قاعدة البيانات ======
# ====== تحديث إعدادات الاتصال بقاعدة البيانات ======
def get_db_connection():
    with db_lock:  # قفل الاتصال لضمان أن عملية واحدة فقط تستطيع الوصول إلى قاعدة البيانات في الوقت ذاته
        conn = sqlite3.connect('database.db', timeout=60)  # زيادة المهلة لتفادي مشكلة القفل
        conn.row_factory = sqlite3.Row
        
        # تفعيل وضع WAL للـ journal_mode لزيادة التزامن
        conn.execute("PRAGMA journal_mode=WAL;")  # وضع الـ journal_mode إلى WAL
        conn.execute("PRAGMA synchronous=NORMAL;")  # تعديل إعدادات التزامن (اختياري)

        return conn


# ====== تحديث الجدول بإضافة الأعمدة المفقودة ======
import time

# ====== تحديث الجدول بإضافة الأعمدة المفقودة ======
def update_table():
    retries = 5
    for i in range(retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # إضافة الأعمدة المفقودة (تأكد من أن الأعمدة جميعها موجودة)
            cursor.execute("ALTER TABLE applications ADD COLUMN interview_status TEXT;")
            cursor.execute("ALTER TABLE applications ADD COLUMN interview_date TEXT;")
            cursor.execute("ALTER TABLE applications ADD COLUMN interview_time TEXT;")
            conn.commit()
            print("تم إضافة الأعمدة بنجاح.")
            conn.close()
            return
        except sqlite3.OperationalError as e:
            print(f"خطأ أثناء التعديل: {e}")
            time.sleep(2)  # الانتظار لثواني قبل المحاولة مرة أخرى
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
    return render_template('employment_interviews.html', applications=applications)

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
        interview_time TEXT
    )
    ''')
    conn.commit()
    conn.close()

# استدعاء دالة إنشاء الجدول عند بداية تشغيل التطبيق
create_table()

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

        # البيانات الجديدة
        interview_status = data.get('interviewStatus')
        interview_date = data.get('interviewDate')
        interview_time = data.get('interviewTime')

        conn = get_db_connection()
        cursor = conn.cursor()

        # حذف بيانات قديمة (اختياري)
        cursor.execute("DELETE FROM applications WHERE name = ? AND phone = ?", (name, phone))

        # إدخال البيانات
        cursor.execute(''' 
            INSERT INTO applications 
            (name, nationality, birth_date, religion, gender, marital_status, address, phone, currently_employed, interview_status, interview_date, interview_time) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            interview_time
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('employment_interviews_page'))


    except Exception as e:
        print(f"خطأ أثناء الحفظ: {e}")
        return "حدث خطأ أثناء إرسال الطلب"


# دالة حذف طلب التوظيف
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
