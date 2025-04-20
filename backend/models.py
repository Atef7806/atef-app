# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    requirements = db.Column(db.Text)
    posted_date = db.Column(db.String(100))  # نستخدم نص زي الموجود في SQLite

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100))
    cv_text = db.Column(db.Text)
    cv_path = db.Column(db.String(200))
    created_at = db.Column(db.String(100))

class AIEvaluation(db.Model):
    __tablename__ = 'ai_evaluations'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    evaluation_date = db.Column(db.String(100))
    match_percentage = db.Column(db.Float)
    notes = db.Column(db.Text)

    application = db.relationship('Application', backref='ai_evaluations')

class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    interviewer = db.Column(db.String(100))
    interview_date = db.Column(db.String(100))
    interview_time = db.Column(db.String(100))
    notes = db.Column(db.Text)
    result = db.Column(db.String(100))

    application = db.relationship('Application', backref='interviews')
