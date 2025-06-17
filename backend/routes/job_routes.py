from flask import Blueprint, request, render_template, redirect, url_for, flash
from models import db, Job
from datetime import datetime
from flask import Blueprint, render_template

bp = Blueprint('job_routes', __name__)

# عرض جميع الوظائف
@bp.route('/jobs')
def jobs():
    jobs_list = Job.query.all()  # جلب جميع الوظائف من قاعدة البيانات
    return render_template('jobs.html', jobs=jobs_list)

# إضافة وظيفة جديدة
@bp.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        department = request.form['department']
        location = request.form['location']
        requirements = request.form['requirements']

        # إنشاء وظيفة جديدة
        new_job = Job(
            title=title,
            description=description,
            department=department,
            location=location,
            requirements=requirements,
            posted_date=datetime.utcnow()
        )

        try:
            db.session.add(new_job)
            db.session.commit()
            flash("تم إضافة الوظيفة بنجاح!", "success")
            return redirect(url_for('job_routes.jobs'))  # إعادة التوجيه إلى صفحة الوظائف
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء إضافة الوظيفة: {e}", "error")
            return redirect(url_for('job_routes.add_job'))  # إعادة التوجيه إلى صفحة إضافة وظيفة جديدة

    return render_template('add_job.html')  # عرض نموذج إضافة وظيفة جديدة
