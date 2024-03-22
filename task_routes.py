from flask import Blueprint, jsonify, request
from models import Task, User
from app import db

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/<string:user_id>/tasks', methods=['GET'])
# returns: tasks
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    if not tasks:
        return jsonify({'message': 'Invalid user_id or no tasks found!'}), 404
    tasks = [{'task_id': task.id, 'content': task.content,
              'created_at': task.created_at, 'due_date': task.due_date,
              'completed': task.completed} for task in tasks]
    return jsonify({'tasks': tasks}), 200

@task_bp.route('/api/<string:user_id>/add-task', methods=['POST'])
# params: content
# returns: task created
def add_task(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Invalid user_id!'}), 404
    try:
        data = request.get_json()
        content = data['content']
        new_task = Task(user_id=user_id, content=content)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully!'}), 201
    except KeyError:
        return jsonify({'message': 'Invalid request! Missing content parameter.'}), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred while creating the task.', 'error': str(e)}), 500

@task_bp.route('/api/<string:user_id>/update-task-contents/<string:task_id>', methods=['PATCH'])
# params: new_content
# returns: task updated
def update_task_contents(user_id, task_id):
    try:
        data = request.get_json()
        if not 'new_content' in data:
            return jsonify({'message': 'Invalid request! Missing new_content parameter.'}), 400
        
        new_content = data['new_content']
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        
        if not task:
            return jsonify({'message': 'Invalid user_id or task_id!'}), 404

        task.content = new_content
        db.session.commit()
        return jsonify({'message': 'Task updated successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while updating the task.', 'error': str(e)}), 500

@task_bp.route('/api/<string:user_id>/complete-task/<string:task_id>', methods=['PATCH'])
# returns: task completed
def task_completed(user_id, task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({'message': 'Invalid user_id or task_id!'}), 404
        task.completed = True
        db.session.commit()
        return jsonify({'message': 'Task completed successfully!'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while completing the task.', 'error': str(e)}), 500




