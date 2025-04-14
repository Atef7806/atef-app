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
    return render_template('employment application.html')

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




if __name__ == '__main__':
    app.run(debug=True)
