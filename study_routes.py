from flask import Blueprint, jsonify, request
from models import User
from app import db, bcrypt
import re
from datetime import datetime

study_bp = Blueprint('study', __name__)

import time
from functools import wraps



@study_bp.route('/api/<string:user_id>/phone-connected', methods=['GET'])
def phone_connected(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.phone_in_box_current = True
    user.last_phone_in_box_time = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Phone connected!'}), 200

@study_bp.route('/api/<string:user_id>/phone-disconnected', methods=['GET'])
def phone_disconnected(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user.phone_in_box_current:
        last_phone_in_box_time = user.last_phone_in_box_time
        time_connected = (datetime.now().timestamp()) - last_phone_in_box_time.timestamp()
        user.study_hours_today += time_connected
        db.session.commit()

    if time_connected >= user.study_goal_session:
        db.session.commit()
        return jsonify({'message': 'Phone disconnected!', 'time-studied': time_connected, 'level': user.level}), 200
    
    if user.study_hours_today >= user.study_goal:
        db.session.commit()
        return jsonify({'message': 'Phone disconnected!', 'time-studied': time_connected, 'level': user.level}), 200
    
    return jsonify({'message': 'Phone disconnected!', 'time-studied': time_connected}), 200
    


    user.phone_in_box_current = False
    db.session.commit()
    return jsonify({'message': 'Phone disconnected!', 'time-studied': ''}), 200
