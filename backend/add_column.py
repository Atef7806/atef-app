import sqlite3

def get_db_connection():
    conn = sqlite3.connect('recruitment.db')
    conn.row_factory = sqlite3.Row
    return conn

try:
    conn = get_db_connection()
    cursor = conn.cursor()

    # إيقاف المفاتيح الأجنبية مؤقتًا
    cursor.execute("PRAGMA foreign_keys=off;")

    # إنشاء الجدول الجديد
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        department TEXT,  -- إضافة العمود الجديد
        location TEXT NOT NULL,
        requirements TEXT NOT NULL,
        posted_date TEXT NOT NULL
    );
    """)

    # نسخ البيانات من الجدول القديم إلى الجدول الجديد
    cursor.execute("""
    INSERT INTO jobs_new (id, title, description, department, location, requirements, posted_date)
    SELECT id, title, description, department, location, requirements, posted_date FROM jobs;
    """)

    # حذف الجدول القديم
    cursor.execute("DROP TABLE jobs;")

    # تغيير اسم الجدول الجديد إلى الجدول القديم
    cursor.execute("ALTER TABLE jobs_new RENAME TO jobs;")

    # تفعيل المفاتيح الأجنبية مرة أخرى
    cursor.execute("PRAGMA foreign_keys=on;")

    conn.commit()
    conn.close()
    print("تم إضافة العمود department إلى جدول jobs بنجاح.")
except Exception as e:
    print(f"حدث خطأ أثناء التعديل: {e}")
