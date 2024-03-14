from flask import Blueprint, jsonify, request
from models import User, League, LeagueMembership
from app import db

league_bp = Blueprint('league', __name__)

@league_bp.route('/api/<string:user_id>/create-league', methods=['POST'])
# params: league_name
# returns: league created || error message
def create_league(user_id):
    data = request.get_json()
    league_name = data['league_name']
    league = League(name=league_name)
    db.session.add(league)
    db.session.commit()
    league_membership = LeagueMembership(user_id=user_id, league_id=league.id)
    db.session.add(league_membership)
    db.session.commit()
    return jsonify({'message': 'League created successfully!'}), 201

@league_bp.route('/api/<string:user_id>/leagues', methods=['GET'])
# returns: leagues
def leagues(user_id):
    leagues = LeagueMembership.query.filter_by(user_id=user_id).all()
    leagues = [{'league_id': league.league_id} for league in leagues]
    return jsonify({'leagues': leagues}), 200

@league_bp.route('/api/<string:user_id>/join-league', methods=['POST'])
# params: league_id
# returns: league joined || error message
def join_league(user_id):
    data = request.get_json()
    league_id = data['league_id']
    league_membership = LeagueMembership(user_id=user_id, league_id=league_id)
    db.session.add(league_membership)
    db.session.commit()
    return jsonify({'message': 'League joined successfully!'}), 201

@league_bp.route('/api/<string:user_id>/leave-league/<string:league_id>', methods=['DELETE'])
# returns: league left
def leave_league(user_id, league_id):
    league_membership = LeagueMembership.query.filter_by(user_id=user_id, league_id=league_id).first()
    db.session.delete(league_membership)
    db.session.commit()
    return jsonify({'message': 'League left successfully!'}), 200

@league_bp.route('/api/<string:user_id>/league-members/<string:league_id>', methods=['GET'])
# returns: league members
def league_members(user_id, league_id):
    league_members = LeagueMembership.query.filter_by(league_id=league_id).all()
    league_members = [{'user_id': league_member.user_id} for league_member in league_members]
    return jsonify({'league_members': league_members}), 200


