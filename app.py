from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_companies():
    conn = sqlite3.connect('companies.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies")
    rows = cur.fetchall()
    conn.close()
    return rows

# 🏠 الصفحة الرئيسية تعرض الشركات
@app.route('/')
def companies():
    all_companies = get_companies()
    return render_template('companies.html', companies=all_companies)

# ✅ روابط صفحات أخرى:
@app.route('/contact-us')
def contact_us():
    return render_template('contact us.html')

@app.route('/customer-support')
def customer_support():
    return render_template('costomer support.html')

@app.route('/employment-application')
def employment_application():
    return render_template('employment application.html')

@app.route('/employment-interviews')
def employment_interviews():
    return render_template('employment interviews.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/job-management')
def job_management():
    return render_template('job management.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/logout')
def logout():
    return render_template('log out.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/manage-applicants')
def manage_applicants():
    return render_template('manage applicants.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/smart-search')
def smart_search():
    return render_template('smart search.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/weblog')
def weblog():
    return render_template('weblog.html')

@app.route('/who-are-you')
def who_are_you():
    return render_template('who are you.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('who are you.html')

@app.route('/account-management')
def account_management():
    return render_template('account_management.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/employment-application')
def employment_application():
    return render_template('employment application.html')
