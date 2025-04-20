from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, UPLOAD_FOLDER

# إنشاء التطبيق
app = Flask(__name__)
CORS(app)

# تحميل الإعدادات
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة البيانات
db = SQLAlchemy(app)

# استيراد وتسجيل الراوتات (هنضيفهم بعدين)
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.application_routes import application_bp
from routes.interview_routes import interview_bp

app.register_blueprint(auth_bp)
app.register_blueprint(job_bp)
app.register_blueprint(application_bp)
app.register_blueprint(interview_bp)

if __name__ == "__main__":
    app.run(debug=True)
