from models import db, User
from app import app  # تأكد أن app هو التطبيق الرئيسي الذي قمت بتعريفه

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()
    print("✅ Database created successfully from models.py!")

    # إدخال المستخدم الافتراضي
    new_user = User(username="admin", password="admin123", role="admin", full_name="Admin User", email="admin@example.com", user_type="employer")
    db.session.add(new_user)
    db.session.commit()
    print("✅ Default user created successfully!")
