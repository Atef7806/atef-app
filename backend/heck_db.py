import sqlite3

def show_all_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # جلب أسماء الجداول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("الجداول الموجودة في قاعدة البيانات:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("لا توجد جداول في قاعدة البيانات.")

    conn.close()

# مسار قاعدة البيانات
show_all_tables('recruitment.db')  # استبدل بالمسار الصحيح لقاعدة بياناتك


def show_table_content(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")  # طباعة أول 5 صفوف للتجربة
    rows = cursor.fetchall()

    if rows:
        print(f"بيانات من جدول {table_name}:")
        for row in rows:
            print(row)
    else:
        print(f"الجدول {table_name} فارغ.")

    conn.close()

# مثال
show_table_content('backend/database.db', 'applications')


def show_table_columns(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    if columns:
        print(f"أعمدة الجدول {table_name}:")
        for col in columns:
            print(f"- {col[1]}")
    else:
        print(f"مافيش أعمدة في الجدول {table_name}")

    conn.close()

# استخدمها كده:
show_table_columns('backend/database.db', 'applications')
