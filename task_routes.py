from flask import Blueprint, jsonify, request
from models import Task
from app import db

task_bp = Blueprint('task', __name__)

@task_bp.route('/api/<string:user_id>/tasks', methods=['GET'])
# returns: tasks
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    tasks = [{'task_id': task.id, 'contents': task.content,
              'created_at': task.created_at, 'due_date': task.due_date,
              'completed': task.completed} for task in tasks]
    return jsonify({'tasks': tasks}), 200

@task_bp.route('/api/<string:user_id>/add-task', methods=['POST'])
# params: content
# returns: task created
def add_task(user_id):
    data = request.get_json()
    content = data['contents']
    task_id = data['task_id']
    if 'due_date' in data:
        due_date = data['due_date']
        new_task = Task(id=task_id, user_id=user_id, content=content, due_date=due_date)
    new_task = Task(id=task_id, user_id=user_id, content=content)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully!'}), 201

@task_bp.route('/api/<string:user_id>/update-task-contents/<string:task_id>', methods=['PATCH'])
# params: new_content
# returns: task updated 
def update_task_contents(user_id, task_id):
    data = request.get_json()
    if not 'new_content' in data:
        return jsonify({'message': 'Invalid request!'}), 400
    
    new_content = data['new_content']
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    task.content = new_content
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'}), 200

@task_bp.route('/api/<string:user_id>/delete-task/<string:task_id>', methods=['DELETE'])
# returns: task completed
def task_deleted(user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'}), 200

## todo- get incomplete tasks
## todo - get complete tasks
## todo - get top incomplete task
## todo - delete task
## todo - get all tasks




