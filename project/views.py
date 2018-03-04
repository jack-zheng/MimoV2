from project import app
from flask import request, abort, jsonify, render_template,redirect, url_for
from project.models import Task
from datetime import datetime
from project.forms import SampleForm

json_time_fields = ['start', 'end', 'updatetime']


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World'


@app.route('/index', methods=['GET'])
def index():
    tasks = Task.get_all()[:10]
    return render_template('index.html', tasks=tasks)


@app.route('/htmldemo', methods=['GET', 'POST'])
def html_demo():
    form = SampleForm()
    if form.validate_on_submit():
        return redirect(url_for('redirect_page'))
    return render_template('html_demo.html', form=form)


@app.route('/cssdemo', methods=['GET', 'POST'])
def css_demo():
    return render_template('css_demo.html')


@app.route('/headfirstjs', methods=['GET'])
def head_first_js():
    return render_template('head_first_js.html')


@app.route('/gumball', methods=['GET'])
def gumball():
    return render_template('gumball.html')


@app.route('/canvas', methods=['GET'])
def canvas():
    return render_template('canvas.html')


@app.route('/redirect', methods=['GET', 'POST'])
def redirect_page():
    return render_template('redirect.html')


@app.route('/jsdemo', methods=["GET"])
def handle_data():
    return render_template('js_demo.html')


@app.route('/todo/api/v1/tasks', methods=['POST'])
def post_task():
    if not request.get_json():
        abort(400, "Title should not be empty")

    if 'title' not in request.get_json():
        abort(400, "Request not in json format")

    # new a task and save it to db, return it's detail as response
    request_json = request.get_json()
    # remove empty pairs
    remove_empty_pair(request_json)
    # create a new task to store the post value
    task = json_to_task_obj_converter(request_json)

    task.save()

    response = jsonify(task_obj_to_json_converter(task))
    response.status_code = 201
    return response


def remove_empty_pair(json_data):
    for key in list(json_data):
        if not json_data.get(key):
            json_data.pop(key)


def json_to_task_obj_converter(request_json):
    task = Task()
    for key in request_json:
        if key in json_time_fields:
            parsed_time = datetime.strptime(request_json.get(key), "%Y-%m-%d %H:%M")
            if key == json_time_fields[0]:
                task.start_timestamp = parsed_time
            elif key == json_time_fields[1]:
                task.end_timestamp = parsed_time
            elif key == json_time_fields[2]:
                task.update_timestamp = parsed_time
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
        if task.__getattribute__(column.key):
            if column.key == Task.start_timestamp.key:
                task_json[json_time_fields[0]] = datetime.strftime(task.start_timestamp, "%Y-%m-%d %H:%M")
            elif column.key == Task.end_timestamp.key:
                task_json[json_time_fields[1]] = datetime.strftime(task.end_timestamp, "%Y-%m-%d %H:%M")
            elif column.key == Task.update_timestamp.key:
                task_json[json_time_fields[2]] = datetime.strftime(task.update_timestamp, "%Y-%m-%d %H:%M")
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
