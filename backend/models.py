from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # معرف فريد لكل طلب
    name = db.Column(db.String(100))  # اسم الشخص المتقدم للوظيفة
    interview_date = db.Column(db.String(50))  # تاريخ المقابلة
    interview_time = db.Column(db.String(50))  # وقت المقابلة
    interview_status = db.Column(db.String(50))  # حالة المقابلة (مثل "معلقة" أو "مكتملة")
    cv_path = db.Column(db.String(255))  # مسار السيرة الذاتية
    interview_link = db.Column(db.String(255))  # رابط المقابلة (إذا كانت عبر الإنترنت)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ ووقت تقديم الطلب (مضاف حديثًا)

    def __repr__(self):
        return f'<Application {self.name}>'
