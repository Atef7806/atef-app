import sqlite3

# الاتصال بقاعدة البيانات (غالبًا اسمها كده، لكن لو مختلف قوله لي)
conn = sqlite3.connect('applications.db')  # غيّر الاسم لو مختلف

cursor = conn.cursor()

try:
    # محاولة إضافة عمود جديد اسمه cv_path
    cursor.execute("ALTER TABLE applications ADD COLUMN cv_path TEXT")
    print("✅ تم إضافة العمود cv_path بنجاح.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️ العمود موجود بالفعل.")
    else:
        print(f"❌ خطأ أثناء الإضافة: {e}")

conn.commit()
conn.close()
