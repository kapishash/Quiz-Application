from flask import Flask, request
import os
from app.models import db, User, Quiz
from flask_jwt_extended import JWTManager
from flask_restful import Resource, Api
from app.api import LoginApi, SignupApi, WecomeAPI, ExportDataApi, SubjectApi, cache, UserApi
from app.chapter_api import ChapterApi
from app.quiz_api import QuizApi
from app.question_api import QuestionApi
from app.admin_api import AdminApi
from app.user_api import UserDashboardApi, ExamApi, ResultApi
from app.task import *
from datetime import timedelta, datetime
from app.plots import UserChartApi, AdminBarChartApi, AdminPieChartApi
from flask_caching import Cache
from app.worker import celery
import time



base_dir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'app.sqlite3')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'quiz-app'
app.config['JWT_SECRET_KEY'] = 'quiz-app-jwt'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)


app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = "redis://localhost:6379"
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/1',
    timezone= 'Asia/Kolkata'
)


db.init_app(app)
cache.init_app(app)
api = Api(app)
jwt = JWTManager(app)

app.app_context().push()
# print("Database created")
def add_admin():
    admin_user = User.query.filter_by(email='admin@mail.com').first()
    if not admin_user:
        admin = User(
        email='admin@mail.com',
        password='1234',
        is_admin=True,
        full_name='admin',
        role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        



# @app.route('/test_cache')
# @cache.cached(timeout=20)
# def test_cache():
#     time.sleep(2)
#     return f"Testing is working {datetime.datetime.now()}"

api.add_resource(LoginApi, '/api/login')
api.add_resource(UserApi, '/api/users', '/api/users/<int:user_id>')
api.add_resource(SignupApi, '/api/signup')
api.add_resource(WecomeAPI, '/api/welcome')
api.add_resource(SubjectApi, '/api/subject', '/api/subject/<int:subject_id>')
api.add_resource(ChapterApi, '/api/chapter', '/api/chapter/<int:chapter_id>')
api.add_resource(QuizApi, '/api/quiz', '/api/quiz/<int:quiz_id>')
api.add_resource(QuestionApi, '/api/question', '/api/question/<int:question_id>')
api.add_resource(AdminApi, '/api/admin')
api.add_resource(UserDashboardApi, '/api/user_dash')
api.add_resource(ExamApi, '/api/exam/<int:id>')
api.add_resource(ResultApi, '/api/result/<int:score_id>')
api.add_resource(ExportDataApi, '/api/export/data')
api.add_resource(UserChartApi, "/api/user_chart/image")
api.add_resource(AdminBarChartApi, "/api/admin_bar_chart/image")
api.add_resource(AdminPieChartApi, "/api/admin_pie_chart/image")



if __name__ == "__main__":
    db.create_all()
    print("Database created")
    add_admin()
    app.run(debug=True, port=5001)


