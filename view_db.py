import sqlite3

# الاتصال بقاعدة البيانات (لازم يكون الملف في نفس الفولدر)
conn = sqlite3.connect('companies.db')
cur = conn.cursor()

# تنفيذ الاستعلام لعرض كل البيانات من جدول الشركات
cur.execute("SELECT * FROM companies")
rows = cur.fetchall()

# طباعة النتائج
if rows:
    print("بيانات الشركات:")
    for row in rows:
        print(row)
else:
    print("لا توجد بيانات.")

# إغلاق الاتصال
conn.close()
