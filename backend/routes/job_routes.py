# job_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from models import db, Job
from datetime import datetime

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
            return redirect(url_for('job_routes.add_job'))

    return render_template('add_job.html')  # عرض نموذج إضافة وظيفة جديدة

# تعديل وظيفة موجودة
@bp.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)  # جلب الوظيفة من قاعدة البيانات

    if request.method == 'POST':
        job.title = request.form['title']
        job.description = request.form['description']
        job.department = request.form['department']
        job.location = request.form['location']
        job.requirements = request.form['requirements']

        try:
            db.session.commit()  # حفظ التعديلات
            flash("تم تعديل الوظيفة بنجاح!", "success")
            return redirect(url_for('job_routes.jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء تعديل الوظيفة: {e}", "error")
            return redirect(url_for('job_routes.edit_job', job_id=job.id))

    return render_template('edit_job.html', job=job)  # عرض نموذج تعديل الوظيفة

# حذف وظيفة
@bp.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)  # جلب الوظيفة من قاعدة البيانات

    try:
        db.session.delete(job)  # حذف الوظيفة
        db.session.commit()
        flash("تم حذف الوظيفة بنجاح!", "success")
        return redirect(url_for('job_routes.jobs'))
    except Exception as e:
        db.session.rollback()
        flash(f"حدث خطأ أثناء حذف الوظيفة: {e}", "error")
        return redirect(url_for('job_routes.jobs'))