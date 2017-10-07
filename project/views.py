from project import app
from flask import request, abort, jsonify
from project.models import Task


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/todo/api/v1/tasks', methods=['POST'])
def post_task():
    if not request.get_json() or 'title' not in request.get_json():
        abort(400)

    # new a task and save it to db, return it's detail as response
    request_json = request.get_json()

    title = request_json.get('title')
    desc = 'N/A' if not request_json.get('description') else request_json.get('description')
    status = 'In Progress' if not request_json.get('status') else request_json.get('status')

    new_task = Task(title=title, desc=desc, status=status)
    new_task.save()

    response = jsonify(task_obj_to_json_converter(new_task))
    response.status_code = 201

    return response


@app.route('/todo/api/v1/tasks', methods=['GET'])
def get_tasks():
    all_tasks = Task.get_all();
    results = []
    for task in all_tasks:
        obj = task_obj_to_json_converter(task)
        results.append(obj)
    response = jsonify(results)
    response.status_code = 200
    return response


def task_obj_to_json_converter(task):
    task_json = {
        'id': task.id,
        'title': task.title,
        'description': task.desc,
        'status': task.status
    }
    return task_json


@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        abort(404)
    response = jsonify(task_obj_to_json_converter(task))
    response.status_code = 200
    return response


@app.route('/todo/api/v1/tasks', methods=['PUT'])
def update_task():
    if not request.get_json():
        abort(400)

    if 'id' not in request.get_json():
        abort(400)

    task_id = request.get_json().get('id')
    # query to get task with this special id
    query_task_ret = Task.query.filter_by(id=task_id).first()
    if not query_task_ret:
        abort(404)

    # reset value of search out item and update it with new value
    json_ret = request.get_json()
    if json_ret.get('title'):
        query_task_ret.title = json_ret.get('title')

    if json_ret.get('description'):
        query_task_ret.desc = json_ret.get('description')

    if json_ret.get('status'):
        query_task_ret.status = json_ret.get('status')

    query_task_ret.save()
    # now we only overwrite the value pass and keep others as before

    response = jsonify(task_obj_to_json_converter(query_task_ret))
    response.status_code = 201
    return response


@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    query_task_ret = Task.query.filter_by(id=task_id).first()
    if not query_task_ret:
        abort(404)

    query_task_ret.delete()
    response = jsonify({"Remove": "Success"})
    return response
