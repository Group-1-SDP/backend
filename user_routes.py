from flask import Blueprint, jsonify, request
from models import User
from app import db, bcrypt
import re

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/register', methods=['POST'])
# params: email, username, password
# returns: user_id, username || error message
def register():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, username=username, password=hashed_password)

    user_already_exists = User.query.filter_by(username=username).first()
    if user_already_exists:
        return jsonify({'message': 'User already exists!'}), 400
    
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.search(email_regex,email):
        return jsonify({'message': 'Invalid email!'}), 400

    email_already_exists = User.query.filter_by(email=email).first()
    if email_already_exists:
        return jsonify({'message': 'Email already exists!'}), 400
    
    db.session.add(new_user)
    db.session.commit()

    # return the user id and username
    user = User.query.filter_by(username=username).first()
    return jsonify({'user': {'id': user.id, 'username': user.username}}), 201

@user_bp.route('/api/login', methods=['POST'])
# params: username, password
# returns: logged in || error message
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 400
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password!'}), 400
    
    user = User.query.filter_by(username=username).first()
    return jsonify({'user': {'id': user.id, 'username': user.username}}), 200

@user_bp.route('/api/<int:user_id>/get-user-information', methods=['GET'])
# params: user_id
# returns: user
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    username = user.username
    email = user.email
    progress_today = user.progress_today
    study_hours_today = user.study_hours_today
    study_hours_last_5 = user.study_hours_last_5
    study_goal = user.study_goal
    profile_picture = user.profile_picture
    return jsonify({'user': {'id': user_id, 'username': username,
                              'email': email, 'progress_today': progress_today,
                              'study_hours_today': study_hours_today, 'study_hours_last_5': study_hours_last_5,
                              'study_goal': study_goal, 'profile_picture': profile_picture}}), 200

