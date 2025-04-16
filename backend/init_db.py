import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        nationality TEXT,
        birth_date TEXT,
        religion TEXT,
        gender TEXT,
        marital_status TEXT,
        address TEXT,
        phone TEXT,
        currently_employed TEXT
    )
''')

conn.commit()
conn.close()

print("تم إنشاء قاعدة البيانات بنجاح.")
