import sqlite3
import os

def create_database():
    # حذف قاعدة البيانات القديمة (لو موجودة)
    if os.path.exists("recruitment.db"):
        os.remove("recruitment.db")
        print("🗑️ Old recruitment.db deleted.")

    # إنشاء جديدة
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()

    # جدول الوظائف
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        department TEXT,
        location TEXT,
        requirements TEXT,
        posted_date TEXT
    );
    """)

    # جدول التقديمات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        user_email TEXT,
        cv_text TEXT,
        cv_path TEXT,
        created_at TEXT
    );
    """)

    # تقييمات الذكاء الاصطناعي
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        evaluation_date TEXT,
        match_percentage REAL,
        notes TEXT,
        FOREIGN KEY(application_id) REFERENCES applications(id)
    );
    """)

    # المقابلات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        interviewer TEXT,
        interview_date TEXT,
        interview_time TEXT,
        notes TEXT,
        result TEXT,
        FOREIGN KEY(application_id) REFERENCES applications(id)
    );
    """)

    # المستخدمين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("✅ recruitment.db created successfully!")

# إنشاء القاعدة
create_database()
