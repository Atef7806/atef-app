from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User  # تأكد من استيراد نموذج المستخدم بشكل صحيح

# تعريف Blueprint
auth_bp = Blueprint('auth', __name__)

# دالة إنشاء حساب
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # هنا يمكنك إضافة منطق التحقق من النموذج وتخزين بيانات المستخدم
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']
        email = request.form['email']

        # إنشاء المستخدم وتخزينه في قاعدة البيانات
        new_user = User(username=username, password=password, role=role, full_name=full_name, email=email)
        db.session.add(new_user)
        db.session.commit()

        flash('تم إنشاء الحساب بنجاح!', 'success')
        return redirect(url_for('auth.login'))  # إعادة التوجيه لصفحة الدخول بعد النجاح

    return render_template('signup.html')  # عرض نموذج التسجيل
