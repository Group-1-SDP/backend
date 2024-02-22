from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import db
from models import User

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def default_msg():
    return jsonify(
        {
            'message': 'Default Message From the API.'
        }
    )

@api.route('/createUser', methods=['POST'])
def create_user():
    email = request.json.get('email')
    password = request.json.get('password')
    username = request.json.get('username')
    id = request.json.get('id')

    # Create a new user object
    new_user = User(email=email, password=password, username=username, id=id)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Try to GET the new user and return the result (if successful or not)
    try:
        user = User.query.filter_by(id=id).first()
        return jsonify(
            {
                'message': 'User Created Successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                }
            }
        )
    except:
        return jsonify(
            {
                'message': 'User Creation Failed'
            }
        )