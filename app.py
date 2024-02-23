from flask import Flask, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from datetime import datetime
from models import db, User, Task

import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickbox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to supress warning
CORS(app, resources={r"/api/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/api/isAlive', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def is_alive():
    return jsonify({'message': 'Alive!'}), 200

@app.route('/api/register', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def register():
    data = request.get_json()
    email = data['email']
    username = data['username']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password, email=email)

    userAlreadyExists = User.query.filter_by(username=username).first()
    if userAlreadyExists:
        return jsonify({'message': 'User already exists!'}), 409
    
    emailRegex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.search(emailRegex,email):
        return jsonify({'message': 'Invalid email!'}), 400

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password!'}), 401
    else:
        return jsonify({'message': 'Logged in successfully!'}), 200
    

@app.route('/api/addTask', methods=['POST'])
def addTask():
    return jsonify({'message': 'Not Implemented Yet!'}), 200















if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)