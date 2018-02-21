from project import app
from flask import request, abort, jsonify
from project.models import Task
from datetime import datetime


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/todo/api/v1/tasks', methods=['POST'])
def post_task():
    if not request.get_json() or 'title' not in request.get_json():
        abort(400)

    # new a task and save it to db, return it's detail as response
    request_json = request.get_json()
    # create a new task to store the post value
    task = json_to_task_obj_converter(request_json)

    # if no timestamp in task, or timestamp is none, use utc now instead
    if not task.timestamp:
        task.timestamp = datetime.utcnow()

    task.save()

    response = jsonify(task_obj_to_json_converter(task))
    response.status_code = 201
    return response


def json_to_task_obj_converter(request_json):
    task = Task()
    for key in request_json:
        if key == "timestamp":
            task.timestamp = datetime.strptime(request_json.get(key), "%Y-%m-%d")
        else:
            task.__setattr__(key, request_json.get(key))
    return task


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
    task_json = {}
    for column in Task.__table__.columns:
        if column.key == 'timestamp' and task.timestamp:
            task_json[column.key] = datetime.strftime(task.timestamp, "%Y-%m-%d")
        else:
            task_json[column.key] = task.__getattribute__(column.key)

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
        abort(400, 'No json object found')

    if 'id' not in request.get_json():
        abort(400, 'No id attribute found')

    task_id = request.get_json().get('id')
    # query to get task with this special id
    query_task_ret = Task.query.filter_by(id=task_id).first()
    if not query_task_ret:
        abort(404, 'No record with id {} in db'.format(task_id))

    # reset value of search out item and update it with new value
    json_ret = request.get_json()
    for key in json_ret:
        query_task_ret.__setattr__(key, json_ret[key])

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
