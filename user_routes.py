from flask import Blueprint, jsonify, request
from models import User
from app import db, bcrypt
import re

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, username=username, password=hashed_password)

    user_already_exists = User.query.filter_by(username=username).first()
    if user_already_exists:
        return jsonify({'message': 'User already exists.'}), 400
    
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.search(email_regex, email, re.IGNORECASE):
        return jsonify({'message': 'Invalid email.'}), 400

    email_already_exists = User.query.filter_by(email=email).first()
    if email_already_exists:
        return jsonify({'message': 'Email already exists.'}), 400
    
    db.session.add(new_user)
    db.session.commit()

    # return the user id and username
    user = User.query.filter_by(username=username).first()
    return jsonify({'id': user.id, 'username': user.username}), 201

@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 400

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password!'}), 400
    
    return jsonify({'id': user.id, 'username': user.username}), 200

@user_bp.route('/api/<string:user_id>/information', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    return jsonify({'user': {'id': user_id, 'username': user.username,
                              'email': user.email, 'progress_today': user.progress_today,
                              'study_hours_today': user.study_hours_today, 'study_hours_last_5': user.study_hours_last_5,
                              'study_goal': user.study_goal, 'profile_picture': user.profile_picture}}), 200

@user_bp.route('/api/<string:user_id>/update', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    email = data.get('email', '')
    username = data.get('username', '')
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message': 'User not found.'}), 404

    if old_password:
        if not bcrypt.check_password_hash(user.password, old_password):
            return jsonify({'message': 'Invalid password!'}), 400

    if new_password:
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    if email:
        email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.search(email_regex, email):
            return jsonify({'message': 'Invalid email.'}), 400

        email_already_exists = User.query.filter_by(email=email).first()
        if email_already_exists and email_already_exists.id != user_id:
            return jsonify({'message': 'Email already exists.'}), 400

        user.email = email

    if username:
        username_already_exists = User.query.filter_by(username=username).first()
        if username_already_exists and username_already_exists.id != user_id:
            return jsonify({'message': 'Username already exists.'}), 400

        user.username = username

    db.session.commit()

    return jsonify({'message': 'User updated successfully!'}), 200

@user_bp.route('/api/debug/user_ids', methods=['GET'])
def get_user_ids():
    users = User.query.all()
    user_ids = [user.id for user in users]
    return jsonify({'user_ids': user_ids}), 200