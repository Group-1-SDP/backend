from flask import Blueprint, jsonify, request
from models import User
from app import db
from datetime import datetime

study_bp = Blueprint('study', __name__)



@study_bp.route('/api/<string:user_id>/phone-connected', methods=['GET'])
def phone_connected(user_id):
    user = User.query.filter_by(id=user_id).first()

    user.phone_in_box_current = True
    user.last_phone_in_box_time = datetime.now()
    db.session.commit()

    return jsonify({'message': 'Phone connected!', 'time_connected': datetime.now()}), 200

@study_bp.route('/api/<string:user_id>/phone-disconnected', methods=['POST'])
def phone_disconnected(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    time_since = data.get('time_since')

    if not time_since:
        return jsonify({'error': 'Invalid request, time_since parameter missing'}), 400

    date_format = "%d/%m/%Y, %H:%M:%S"
    try:
        phone_out_time = datetime.strptime(time_since, date_format)
    except ValueError:
        return jsonify({'error': 'Invalid time_since format'}), 400

    last_phone_in_box_time = user.last_phone_in_box_time
    time_connected = (last_phone_in_box_time - phone_out_time).total_seconds()
    
    if time_connected < 0:
        return jsonify({'error': 'Invalid time_since value, it should be before the last phone in box time'}), 400

    study_time_increment = time_connected / 6 

    user.study_hours_today += study_time_increment
    time_studied = user.study_hours_today

    db.session.commit()

    return jsonify({'message': 'Phone disconnected!', 'time_studied': time_studied}), 200