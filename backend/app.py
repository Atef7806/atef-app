from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/companies')
def companies():
    return render_template('companies.html')

@app.route('/seeker-profile')
def seeker_profile():
    return render_template('الملف الشخصي للباحث عن عمل.html')

@app.route('/employment-application')
def employment_application():
    return render_template('employment_application.html')

@app.route('/who-are-you')
def who_are_you():
    return render_template('who are you.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact us.html')

@app.route('/job-management')
def job_management():
    return render_template('job management.html')
@app.route('/manage-applicants')
def manage_applicants():
    return render_template('manage applicants.html')

@app.route('/employment-interviews')
def employment_interviews():
    return render_template('employment interviews.html')

@app.route('/smart-search')
def smart_search():
    return render_template('smart search.html')

@app.route('/account-management')
def account_management():
    return render_template('account management.html')

@app.route('/advertisements')
def advertisements():
    return render_template('advertisements.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/customer-support')
def customer_support():
    return render_template('costomer support.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/log-out')
def log_out():
    return render_template('log out.html')



from flask import request, redirect, url_for
import json  # لتخزين البيانات بشكل مبسط


@app.route('/submit-application', methods=['POST'])
def submit_application():
    application_data = request.form.to_dict()
    
    # نحفظ الطلب في ملف JSON (حل مؤقت بسيط بدل قاعدة بيانات)
    try:
        with open('applications.json', 'r', encoding='utf-8') as f:
            all_apps = json.load(f)
    except FileNotFoundError:
        all_apps = []

    all_apps.append(application_data)

    with open('applications.json', 'w', encoding='utf-8') as f:
        json.dump(all_apps, f, ensure_ascii=False, indent=4)

    return redirect(url_for('employment_interviews'))


def employment_interviews():
    try:
        with open('applications.json', 'r', encoding='utf-8') as f:
            all_apps = json.load(f)
    except FileNotFoundError:
        all_apps = []

    return render_template('employment interviews.html', applications=all_apps)













def submit_application():
    full_name = request.form.get('fullName')
    nationality = request.form.get('nationality')
    birth_date = request.form.get('birthDate')
    religion = request.form.get('religion')
    gender = request.form.get('gender')
    marital_status = request.form.get('maritalStatus')

    # بيانات الاتصال
    address = request.form.get('address')
    phone = request.form.get('phone')
    currently_employed = request.form.get('currentlyEmployed')

    # طباعة للتجربة
    print("====== طلب توظيف جديد ======")
    print(f"الاسم: {full_name}, الجنسية: {nationality}, يعمل حالياً: {currently_employed}")

    # عرض صفحة نجاح
    return render_template('application_success.html', name=full_name)





# بيانات تجريبية
jobs_list = [
    {
        "title": "مطور ذكاء اصطناعي",
        "company": "شركة المستقبل",
        "image": "https://source.unsplash.com/random/800x600?ai",
        "salary": "25,000 - 30,000 ر.س",
        "location": "الرياض",
        "tags": ["AI", "Python", "Machine Learning"],
        "description": "تطوير أنظمة الذكاء الاصطناعي المتقدمة"
    },
    ...
]


def jobs():
    query = request.args.get('q', '')
    if query:
        results = [job for job in jobs_list if query in job['title']]
    else:
        results = jobs_list
    return render_template('jobs.html', jobs=results, query=query)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

