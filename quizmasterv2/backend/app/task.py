from app.worker import celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from app.models import User, Quiz, Score
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
import os
import csv
from flask import Response

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
    sender.add_periodic_task(10.0, daily_reminder.s(), name='daily report every 10 sec',)
    sender.add_periodic_task(10.0, monthly_report.s(), name='monthly report at every 10 sec ',)

    
    
    # hour=19, minute=30
    sender.add_periodic_task(
        crontab(hour=19, minute=30),
        daily_reminder.s(),
        name='daily_reminder when new quizz is added mail at 07:30 pm',
    )

    sender.add_periodic_task(
        crontab(day_of_month="1", month_of_year="*"),
        monthly_report.s(),
        name='monthly report ',
    )

@celery.task
def test(arg):
    print(arg)

@celery.task
def add(x, y):
    z = x + y
    print(z)

def send_mail(email, subject, email_content, attachment=None):
    # Define email server and credentials
    smtp_server_host = "localhost"
    smtp_port = 1025
    sender_email = "admin@mail.com"
    sender_password = ""

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject

    msg.attach(MIMEText(email_content, "html"))

    if attachment:
        
        with open(attachment, "rb") as attachment_data:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data.read())
            encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" %os.path.basename(attachment))

        msg.attach(part)


    server = smtplib.SMTP(host=smtp_server_host, port=smtp_port)
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("Mail sent Successfully")

@celery.task
def daily_reminder():

    users = User.query.filter_by(is_admin=False).all()

    today_730_pm = datetime.now().replace(hour=19, minute=30, second=0, microsecond=0)
    yesterday_730_pm = today_730_pm - timedelta(days=1)
    # print(yesterday_730_pm)
    new_quizzes = Quiz.query.filter(
                                    Quiz.created_at >= yesterday_730_pm,
                                    Quiz.created_at < today_730_pm
                                    ).all()

    if len(new_quizzes) > 0:
        for user in users:
            msg = f'<h1>Hello, { user.full_name }! New Quiz has been added, please visit the website. </h1>'
            send_mail(email = user.email, email_content = msg, subject = "Daily Reminder")
    print("Daily Reminder sent!")
    

    # print(new_quizzes)
    # print(yesterday_730_pm)
    # print(today_730_pm)
    # return "hiiiiiii"
    # print("Daily reminder")


def get_html_report(username, data):
    with open("app/report.html", "r") as file:
        jinja_template = Template(file.read())
        html_report = jinja_template.render(username=username, data=data)

    return html_report

def generate_monthly_report(user):
    # last month
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    today = datetime.now()
    first_day_current_month = today.replace(day=1)     
    last_month_end = first_day_current_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)


    # current day

    # today = datetime.now()
    # month_start = today.replace(day=1)  
    # next_month = (month_start + timedelta(days=31)).replace(day=1)  
    # month_end = next_month - timedelta(days=1) 

    # Get all scores in the current month
    scores = Score.query.filter(
        Score.user_id == user.id,
        Quiz.created_at >= last_month_start,
        Quiz.created_at <= last_month_end
    ).all()

    total_quizzes = len(scores)
    average_score = sum([s.percentage for s in scores]) / total_quizzes if total_quizzes > 0 else 0

    # Fetch ranking logic (example: ranking based on percentage)
    rankings = Score.query.order_by(Score.percentage.desc()).all()
    user_rank = next((index + 1 for index, s in enumerate(rankings) if s.user_id == user.id), None)

    report_data = {
        "name": user.full_name,
        "email": user.email,
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "ranking": user_rank if user_rank else "N/A",
        "scores": scores,
        "month": last_month.strftime("%B %Y")
    }

    return report_data




@celery.task
def monthly_report():
    users = User.query.filter_by(is_admin=False).all()
    
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    

    for user in users:
        report_data = generate_monthly_report(user)
        html_report = get_html_report(user.full_name, report_data)

        send_mail(
            email=user.email,
            email_content=html_report,
            subject=f"Monthly Quiz Report - {last_month.strftime('%B %Y')}"
        )

    print("Monthly reports sent successfully.")

@celery.task
def export_users_csv(quiz_data):
    
    file_path = "data.csv"

    with open(file_path, 'w', newline='') as csv_file:
        fieldnames = ['Name', 'Email', 'total_quizzes', 'average_score']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(quiz_data)

    return file_path