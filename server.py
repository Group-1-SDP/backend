from flask import Flask, request, jsonify
from flask_sqlalchemy  import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from datetime import datetime
from models import db

from user_routes import user_bp
from task_routes import task_bp
from friends_routes import friends_bp
from study_routes import study_bp

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

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(task_bp)
app.register_blueprint(friends_bp)
app.register_blueprint(study_bp)

# SocketIO
@app.route("/websocket/phoneConnected", methods=['POST'])
def phoneConnected():
    socketio.emit('phoneConnected')
    return jsonify({'message': 'Phone connected!'}), 200

@app.route("/websocket/phoneDisconnected", methods=['POST'])
def phoneDisconnected():
    socketio.emit('phoneDisconnected')
    return jsonify({'message': 'Phone disconnected!'}), 200

@app.route("/websocket/study-goal-reached", methods=['GET'])
def studyGoalReached():
    socketio.emit('task-complete')
    return jsonify({'message': 'Rewarded!'}), 200

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
    socketio.run(app, debug=True)
