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
    time_studied = data['time_studied']

    user.study_hours_today = time_studied
    print(user.study_hours_today)
    db.session.commit()

    return jsonify({'message': 'Phone disconnected!'}), 200