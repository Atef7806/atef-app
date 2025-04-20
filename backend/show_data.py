import sqlite3

def show_all_data():
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('recruitment.db')  # تأكد من أن اسم قاعدة البيانات صحيح
    cursor = conn.cursor()

    # الحصول على جميع الجداول في قاعدة البيانات
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # عرض البيانات من كل جدول
    for table in tables:
        table_name = table[0]
        print(f"\nالبيانات في جدول {table_name}:")
        
        # استعلام للحصول على البيانات من الجدول
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print(f"الجدول {table_name} فارغ أو لا يحتوي على بيانات.")
    
    # إغلاق الاتصال
    conn.close()

# استدعاء دالة عرض البيانات
show_all_data()
