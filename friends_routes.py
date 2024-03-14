from flask import Blueprint, jsonify, request
from models import User, Friendship
from app import db

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/api/<string:user_id>/add-friend', methods=['POST'])
# params: friend_username
# returns: friend added || error message
def add_friend(user_id):
    data = request.get_json()
    friend_username = data['friend_username']
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        return jsonify({'message': 'User does not exist!'}), 400

    friendship = Friendship(user_id=user_id, friend_id=friend.id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify({'message': 'Friend added successfully!'}), 201

@friends_bp.route('/api/<string:user_id>/get-friends', methods=['GET'])
# returns: friends
def get_friends(user_id):
    friends = Friendship.query.filter_by(user_id=user_id).all()
    friends = [{'friend_id': friend.friend_id} for friend in friends]
    return jsonify({'friends': friends}), 200

@friends_bp.route('/api/<string:user_id>/remove-friend/<string:friend_id>', methods=['DELETE'])
# returns: friend removed
def remove_friend(user_id, friend_id):
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({'message': 'Friend removed successfully!'}), 200