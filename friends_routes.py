from flask import Blueprint, jsonify, request
from models import User
from app import db

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/api/<string:user_id>/add-friend', methods=['POST'])
# params: friend_username
# returns: friend added || error message
def add_friend(user_id):
    data = request.get_json()
    friend_username = data['friend_username']
    friend = User.query.filter_by(username=friend_username).first()
    current_user = User.query.filter_by(id=user_id).first()
    if not friend:
        return jsonify({'message': 'User does not exist!'}), 400

    if friend == current_user:
        return jsonify({'message': 'You cannot add yourself as a friend!'}), 400
    
    if friend in current_user.friends:
        return jsonify({'message': f'{friend.username} is already your friend!'}), 400

    current_user.friends.append(friend)
    db.session.commit()
    return jsonify({'message': 'Friend added successfully!'}), 201

@friends_bp.route('/api/<string:user_id>/get-friends', methods=['GET'])
# returns: friends
def get_friends(user_id):
    user = User.query.filter_by(id=user_id).first()
    friends = user.friends

    if not friends:
        return jsonify({'message': 'No friends found!'}), 400

    friends = [{'friend_id': friend.id, 'friend_username': friend.username, 'friend_progress': friend.progress_today, 
                'friend_profile_picture': friend.profile_picture, 'friend_level': friend.level} for friend in friends]
    return jsonify({'friends': friends}), 200

@friends_bp.route('/api/<string:user_id>/remove-friend/<string:friend_id>', methods=['DELETE'])
# returns: friend remove
def remove_friend(user_id, friend_id):
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({'message': 'Friend removed successfully!'}), 200