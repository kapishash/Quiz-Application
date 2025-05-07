from flask import request, jsonify, current_app as app, Response, send_file
from flask_restful import Resource, Api
from app.models import db, User, Subject, Score
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_caching import Cache
import json
from app.task import export_users_csv
import io
import os
import time

cache = Cache()


class UserApi(Resource):
    @jwt_required()
    @cache.cached(timeout=10)
    def get(self):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') != 'admin':
            return {'message': 'Access Denied'}, 401
        
        search_query = request.args.get('search', '')

        if search_query:
            users = User.query.filter(User.full_name.ilike(f"%{search_query}%")).all()
        else:
            users = User.query.filter_by(role='user').all() 

        # users = User.query.filter_by(role='user').all() 
        print(users)

        user_list = []

        for user in users:
            user_list.append(user.convert_to_json())
        return user_list, 200

    @jwt_required()
    def delete(self, user_id):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') != 'admin':
            return {'message': 'Access Denied'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found.'}, 404

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully.'}, 200

class LoginApi(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data.get('email')).first()
        # print(user.email)
        if user:
            if user.correct_pass(data.get('password')):
                identity = {"user_id":user.id, "user_role":user.role}
                token = create_access_token(identity=json.dumps(identity))
                return {
                        'message': 'User logged in successfully.',
                        'token':token,
                        'user_name':user.full_name,
                        'user_role':user.role  
                        }, 200
            return {'message': 'Incorrect Password.'}, 400
        return {'message': "User does not exist."}, 404

class SignupApi(Resource):
    def post(self):
        data = request.json
        if not (data.get('name') and data.get('email') and data.get('password') and  data.get('role')):
            return {'message': ' Bad request! All the data fields are required.'}, 400 

        if len(data.get('name').strip()) > 60 or len(data.get('name').strip()) < 4:
            return {'message': 'Length of name should be in between 4 and 60'}, 400 

        if len(data.get('email').strip()) > 60 or "@" not in data.get('email'):
            return {'message': 'Length of email should be 120 and should contain @'}, 400 

        if len(data.get('password').strip()) > 20 or len(data.get('password').strip()) < 4:
            return {'message': 'Length of password should be in between 4 and 20'}, 400 

        if data.get('role').strip() != 'user':
            return {'message': 'Role should be user.'}, 400 


        user = User.query.filter_by(email=data.get('email')).first()
        if user:
            return {'message': "User already exists."}, 400
        new_user = User(
                        full_name=data.get('name'), 
                        email=data.get('email'),
                        password=data.get('password'),
                        role=data.get('role')
                        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User Signed up successfully'}, 201
        
class WecomeAPI(Resource):
    @jwt_required()
    def get(self):
        print(request)
        print(json.loads(get_jwt_identity().get('user_role')))
        print(json.loads(get_jwt_identity().get('user_id')))
        return {'message': 'Hello, This is Quiz App!'}, 200
    def post(self):

        msg= f'Hello! {request.get_json().get("name")}'
        return {'message': msg}, 200


class SubjectApi(Resource):
    @jwt_required()
    def get(self, subject_id=None):
        if subject_id:  
            subject = Subject.query.get(subject_id)
            if subject:
                return subject.convert_to_json(), 200
            return {'message': 'Subject does not exist.'}, 404
        
        search_query = request.args.get('search', '').strip()
        
        if search_query:
            subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        else:
            subjects = Subject.query.all()
        
        sub_list = [sub.convert_to_json() for sub in subjects]
        return sub_list, 200


    @jwt_required()
    def post(self):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') == 'admin':
            data = request.json
            if not (data.get('name') and data.get('about')):
                return {'message': ' Bad request! All the data fields are required.'}, 400 

            if len(data.get('name').strip()) > 120 or len(data.get('name').strip()) < 3:
                return {'message': 'Length of name should be in between 3 and 60'}, 400

            if len(data.get('about').strip()) > 120 or len(data.get('about').strip()) < 3:
                return {'message': 'Length of about section should be in between 3 - 120'}, 400

            subject = Subject.query.filter_by(name=data.get('name').strip()).first()
            if subject:
                return {"message": "Subject already exists."}, 409

            new_subject = Subject(
                            name=data.get('name'), 
                            about=data.get('about')
                            )
            db.session.add(new_subject)
            db.session.commit()
            return {'message': 'Subject added successfully.'}, 201
        return {'message': 'Access Denied'}, 403



    @jwt_required()
    def put(self, subject_id):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') == 'admin':
            data = request.json
            if not (data.get('name') and data.get('about')):
                return {'message': ' Bad request! All the data fields are required.'}, 400 
            

        
            subject = Subject.query.get(subject_id)
            if subject:
                subject.name = data.get('name').strip() if data.get('name') else subject.name
                subject.about = data.get('about').strip() if data.get('about') else subject.about
                db.session.commit()
                return {'message': 'Subject updated successfully.'}, 200 
            return {'message': 'Subject does not exists.'}, 404 
        return {'message': 'Access Denied'}, 403

    @jwt_required()
    def delete(self, subject_id):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') == 'admin':

            subject = Subject.query.get(subject_id)
            if subject:
                db.session.delete(subject)
                db.session.commit()
                return {'message': 'Subject Deleted successfully.'}, 200 
            return {'message': 'Subject does not exists.'}, 404
        return {'message': 'Access Denied'}, 403

        
class ExportDataApi(Resource):
    @jwt_required()
    def get(self):
        current_user = json.loads(get_jwt_identity())
        if current_user.get('user_role') != 'admin':
            return {'message': 'Access Denied'}, 401

        users = User.query.filter_by(is_admin=0).all()
        quiz_data = []

        for user in users:
            total_quizzes = Score.query.filter_by(user_id=user.id).count()
            avg_score = db.session.query(db.func.avg(Score.percentage)).filter_by(user_id=user.id).scalar()
            avg_score = round(avg_score, 2) if avg_score else 0  

            quiz_data.append({
                "Name": user.full_name,
                "Email": user.email,
                "total_quizzes": total_quizzes,
                "average_score": avg_score
            })

        task = export_users_csv.apply_async(args=[quiz_data])


        while not task.ready():
            time.sleep(1) 
        file_path = task.result  

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name="data.csv", mimetype='text/csv')

        return {"message": "File generation failed"}, 500
