from flask import Flask, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from datetime import datetime
from models import db, User, Task

import re

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
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
    data = request.get_json()
    username = data['username']
    task_id = data['task_id']
    date = datetime.utcnow()
    contents = data['contents']

    # Check the user we're adding task for exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404

    new_task = Task(task_id=task_id, user_with_task=username, date=date, contents=contents)

    db.session.add(new_task)
    db.session.commit()

    return jsonify({'message': 'New task added!'}), 201

@app.route('/api/getUserTasks', methods=['POST'])
def getUserTasks():
    data = request.get_json()
    username = data['username']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    else:
        tasks = Task.query.filter_by(user_with_task=username).all()
        task_list = []
        for task in tasks:
            task_data = {}
            task_data['task_id'] = task.task_id
            task_data['date'] = task.date
            task_data['completed'] = task.completed
            task_data['contents'] = task.contents
            task_list.append(task_data)
        return jsonify({'tasks': task_list}), 200
    
@app.route('/api/getIncompleteUserTasks', methods=['POST'])
def getUncompletedUserTasks():
    data = request.get_json()
    username = data['username']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    else:
        tasks = Task.query.filter_by(user_with_task=username, completed=False).all()
        task_list = []
        for task in tasks:
            task_data = {}
            task_data['task_id'] = task.task_id
            task_data['date'] = task.date
            task_data['completed'] = task.completed
            task_data['contents'] = task.contents
            task_list.append(task_data)
        return jsonify({'tasks': task_list}), 200
    
@app.route('/api/getTopIncompleteTask', methods=['POST'])
def getTopIncompleteTask():
    data = request.get_json()
    username = data['username']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    else:
        tasks = Task.query.filter_by(user_with_task=username, completed=False)
        task = tasks.order_by(Task.date).first()
        if not task:
            return jsonify({'message': 'No incomplete tasks!'}), 404
        else:
            task_data = {}
            task_data['task_id'] = task.task_id
            task_data['date'] = task.date
            task_data['completed'] = task.completed
            task_data['contents'] = task.contents
            return jsonify({'task': task_data}), 200

@app.route('/api/updateTask', methods=['PATCH'])
def updateTask():
    data = request.get_json()
    task_id = data['task_id']
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({'message': 'Task does not exist!'}), 404
    else:
        updated_contents = data['contents'] if bool(data.get('contents')) else task.contents
        updated_completion = bool(data.get('completed'))
        
        new_task = Task.query.filter_by(task_id=task_id).update(dict(contents=updated_contents, completed=updated_completion))
        db.session.commit()
        return jsonify({'message': 'Task updated!'}), 200
    
@app.route("/websocket/phoneConnected", methods=['POST'])
def phoneConnected():
    socketio.emit('phoneConnected', broadcast=True)
    return jsonify({'message': 'Phone connected!'}), 200

@app.route("/websocket/phoneDisconnected", methods=['POST'])
def phoneDisconnected():
    socketio.emit('phoneDisconnected', broadcast=True)
    return jsonify({'message': 'Phone disconnected!'}), 200

@socketio.on('connect')
def handle_connect():
    print('client connected!')

@socketio.on('disconnect')
def handle_disconnect():
    print('client disconnected!')

@socketio.on('boxPhoneConnected')
def handle_box_phone_connected():
    socketio.emit('phoneConnected', broadcast=True)

@socketio.on('boxPhoneDisconnected')
def handle_box_phone_disconnected():
    socketio.emit('phoneDisconnected', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)