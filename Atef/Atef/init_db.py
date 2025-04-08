import sqlite3

# الاتصال بقاعدة البيانات (هينشئها لو مش موجودة)
conn = sqlite3.connect('companies.db')
cur = conn.cursor()

# إنشاء الجدول
cur.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        field TEXT NOT NULL
    )
''')

# إدخال بيانات تجريبية
cur.execute("INSERT INTO companies (name, location, field) VALUES ('شركة 1', 'القاهرة', 'تكنولوجيا')")
cur.execute("INSERT INTO companies (name, location, field) VALUES ('شركة 2', 'الإسكندرية', 'تعليم')")
cur.execute("INSERT INTO companies (name, location, field) VALUES ('شركة 3', 'أسيوط', 'صناعة')")

# حفظ التغييرات
conn.commit()
conn.close()

print("تم إنشاء قاعدة البيانات وإضافة البيانات بنجاح.")
import sqlite3

def init_db():
    connection = sqlite3.connect("users.db")  # اسم قاعدة البيانات
    cursor = connection.cursor()

    # كود إنشاء جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    connection.commit()
    connection.close()
    print("Database and 'users' table created successfully.")

if __name__ == "__main__":
    init_db()
