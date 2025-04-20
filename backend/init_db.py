from models import db
from app import app  # تأكد أن app موجود فعلاً في ملف app.py

with app.app_context():
    db.create_all()
    print("✅ Database created successfully from models.py!")
