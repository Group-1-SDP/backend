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
    
    if not password or not email or not username:
        return jsonify({'message': 'Please fill in everything!'}), 402
    
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, email=email)
    
    userAlreadyExists = User.query.filter_by(username=username).first()
    if userAlreadyExists:
        return jsonify({'message': 'User already exists!'}), 409
    
    emailAlreadyExists = User.query.filter_by(email=email).first()
    if emailAlreadyExists:
        return jsonify({'message': 'Email already in use!'}), 408
    
    emailRegex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.search(emailRegex,email):
        return jsonify({'message': 'Invalid email!'}), 400

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!', 'email': new_user.email, 'username': new_user.username})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data['username']
    password = data['password']
    user = User.query.filter_by(username=username_or_email).first()
    if not user:
        user = User.query.filter_by(email=username_or_email).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password!'}), 401
    else:
        return jsonify({'message': 'Logged in successfully!', 'email': user.email, 'username': user.username}), 200

@app.route('/api/deleteUser', methods=['POST'])
def deleteUser():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid password!'}), 401
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully!'}), 200

@app.route('/api/changePassword', methods=['POST'])
def changePassword():
    data = request.get_json()
    
    username = data['username']
    oldPassword = data['oldPassword']
    newPassword = data.get('newPassword', '').strip()

    if len(newPassword) == 0:
        return jsonify({'message': 'New password cannot be empty!'}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message': 'User does not exist!'}), 404

    if not bcrypt.check_password_hash(user.password, oldPassword):
        return jsonify({'message': 'Old password Incorrect!'}), 401
    
    if bcrypt.check_password_hash(user.password, newPassword):
        return jsonify({'message': 'New password must be different from the old password!'}), 402
    
    if newPassword:
        hashed_password = bcrypt.generate_password_hash(newPassword)
        user.password = hashed_password
    
    db.session.commit()

    return jsonify({'message': 'User password successfully changed!'}), 200

@app.route('/api/updateAccountSettings', methods=['POST'])
def updateAccountSettings():
    data = request.get_json()
    
    username = data['username']
    newUsername = data.get('newUsername', '').strip()
    newEmail = data.get('newEmail', '').strip()

    updated = False
    user = User.query.filter_by(username=username).first()

    if newUsername and newUsername != user.username:
        if User.query.filter_by(username=newUsername).first():
            return jsonify({'message': 'Username already taken!'}), 401
        user.username = newUsername
        updated = True  

    if newEmail and newEmail != user.email:
        if User.query.filter_by(email=newEmail).first():
            return jsonify({'message': 'Email already taken!'}), 402
        emailRegex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.search(emailRegex, newEmail):
            return jsonify({'message': 'Invalid email!'}), 403
        user.email = newEmail
        updated = True  

    if updated:
        db.session.commit()
        return jsonify({'message': 'User account settings successfully updated!'}), 200
    else:
        return jsonify({'message': 'No changes detected to user account settings.'}), 200


@app.route('/api/addTask', methods=['POST'])
def addTask():
    #socketio.emit('task-complete')
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
    socketio.emit('task-complete')
    data = request.get_json()
    task_id = data['task_id']
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({'message': 'Task does not exist!'}), 404
    else:
        updated_contents = data['contents'] if bool(data.get('contents')) else task.contents
        updated_completion = bool(data.get('completed'))
        
        new_task = Task.query.filter_by(task_id=task_id).update(dict(contents=updated_contents, completed=updated_completion))
        # We also want to increment the User's total_tasks_completed
        user = User.query.filter_by(username=task.user_with_task).first()
        user.total_tasks_completed += 1
        db.session.commit()
        return jsonify({'message': 'Task updated!'}), 200

@app.route('/api/getUserDetails', methods=['POST'])
def getUserDetails():
    data = request.get_json()
    username = data['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    else:
        user_data = {}
        user_data['username'] = user.username
        user_data['total_tasks_completed'] = user.total_tasks_completed
        user_data['phone_in_box_time'] = user.phone_in_box_time
        user_data['phone_in_box_rn'] = user.phone_in_box_rn
        user_data['friends'] = user.friends
        return jsonify({'user': user_data}), 200

@app.route('/api/getAllUsers', methods=['GET'])
def getAllUsers():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {}
        user_data['username'] = user.username
        user_data['total_tasks_completed'] = user.total_tasks_completed
        user_data['phone_in_box_time'] = user.phone_in_box_time
        user_data['phone_in_box_rn'] = user.phone_in_box_rn
        user_data['friends'] = user.friends
        user_data['id'] = user.id
        user_list.append(user_data)
    return jsonify({'users': user_list}), 200

@app.route('/api/addFriend', methods=['POST'])
def addFriend():
    data = request.get_json()
    username = data['username']
    friend_to_add_username = data['friend_to_add']
    user = User.query.filter_by(username=username).first()
    friend_to_add = User.query.filter_by(username=friend_to_add_username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    if not friend_to_add:
        return jsonify({'message': 'User with that username not found!'}), 404
    else:
        friends_list = user.friends.split(',')
        if friend_to_add_username in friends_list:
            return jsonify({'message': 'Friend already added!'}), 409
        else:
            friends_list.append(friend_to_add_username)
            user.friends = ','.join(friends_list)
            db.session.commit()
            return jsonify({'message': 'Friend added successfully!'}), 200

@app.route('/api/getFriends', methods=['POST'])
def getFriends():
    data = request.get_json()
    username = data['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User does not exist!'}), 404
    else:
        friends = user.friends.split(',')
        user_has_no_friends = len(friends) == 1 and friends[0] == ''
        if user_has_no_friends:
            return jsonify({'message': 'User has no friends!'}), 404
        else:
            return jsonify({'friends': friends}), 200
     
@app.route("/websocket/phoneConnected", methods=['POST'])
def phoneConnected():
    socketio.emit('phoneConnected')
    return jsonify({'message': 'Phone connected!'}), 200

@app.route("/websocket/phoneDisconnected", methods=['POST'])
def phoneDisconnected():
    socketio.emit('phoneDisconnected')
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

@socketio.on('task-complete')
def handle_task_complete():
    socketio.emit('task-complete', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)